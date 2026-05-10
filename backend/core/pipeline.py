import asyncio
from datetime import datetime, timezone
from typing import List
import httpx
import tenacity
from google.genai import errors as genai_errors
from core.pdf_extractor import extract_text_from_pdf
from core.claim_extractor import extract_claims
from core.web_searcher import search_for_claim
from core.claim_verifier import verify_claim
from utils.job_store import job_store
from utils.rate_limiter import limiter
from api.models import JobStatus, ClaimVerdict, FactCheckReport, ClaimResult
from utils.logger import get_logger

logger = get_logger(__name__)

# Concurrency limit: free tier gemini-2.5-flash allows only 5 RPM
MAX_CONCURRENT = 1


def _friendly_error(exc: BaseException) -> str:
    """Convert low-level exceptions into user-readable messages."""
    # Unwrap tenacity RetryError to its root cause
    if isinstance(exc, tenacity.RetryError):
        cause = exc.last_attempt.exception()
        if cause is not None:
            return _friendly_error(cause)
        return "All retry attempts failed. Please try again."

    # ── Google Gemini API errors ──────────────────────────────────────────
    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, "status_code", None)
        if code == 429:
            return (
                "Gemini API quota exceeded. The free tier of gemini-2.0-flash allows "
                "1,500 requests/day. You may have hit the per-minute limit — "
                "please wait a moment and try again."
            )
        if code in (401, 403):
            return "Gemini API authentication failed. Please check your GOOGLE_API_KEY in the .env file."
        if code == 500:
            return "Gemini API internal error. Please try again in a few moments."
        return f"Gemini API error (HTTP {code}). Please try again."

    if isinstance(exc, genai_errors.ServerError):
        return "Gemini API is temporarily unavailable. Please try again in a few moments."

    # ── Network / DNS errors (httpx) ──────────────────────────────────────
    exc_str = str(exc)
    if "getaddrinfo failed" in exc_str or "Name or service not known" in exc_str:
        return (
            "DNS lookup failed — the server could not reach the Gemini API. "
            "Please check your internet connection and try again."
        )
    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout)):
        return (
            "Network error: unable to connect to the Gemini API. "
            "Please check your internet connection and try again."
        )
    if isinstance(exc, httpx.ReadTimeout):
        return "Request timed out waiting for the Gemini API. Please try again."
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 429:
            return "Gemini API rate limit exceeded. Please wait a minute and try again."
        if exc.response.status_code in (401, 403):
            return "Gemini API authentication failed. Please check your GOOGLE_API_KEY."
        return f"Gemini API returned HTTP {exc.response.status_code}. Please try again."

    # ── Missing API key ───────────────────────────────────────────────────
    if isinstance(exc, EnvironmentError):
        return str(exc)

    # Fallback — log the full type for debugging, show clean message
    logger.debug(f"Unclassified pipeline error ({type(exc).__name__}): {exc_str}")
    return f"Processing failed ({type(exc).__name__}). Please try again or contact support."


async def run_pipeline(job_id: str, pdf_bytes: bytes, filename: str) -> None:
    """Main orchestrator for the 5-step fact-checking pipeline."""
    try:
        # ── Step 1: Extract text ──────────────────────────────────────────
        await job_store.update_status(
            job_id, JobStatus.EXTRACTING_TEXT, 10, "Extracting text from PDF..."
        )
        text = extract_text_from_pdf(pdf_bytes)

        # ── Step 2: Extract claims ────────────────────────────────────────
        await job_store.update_status(
            job_id, JobStatus.EXTRACTING_CLAIMS, 20, "Identifying verifiable claims with AI..."
        )
        raw_claims = await extract_claims(text)

        if not raw_claims:
            # No claims found — complete with empty report
            report = FactCheckReport(
                job_id=job_id,
                filename=filename,
                status=JobStatus.COMPLETED,
                created_at=job_store.get_job(job_id)["created_at"],
                completed_at=datetime.now(timezone.utc),
                summary={v.value: 0 for v in ClaimVerdict},
                summary_note=(
                    "No high-impact verifiable claims (financials, dates, or statistics) were "
                    "identified in this text. This often occurs if the document is primarily "
                    "descriptive, legal boilerplate, or contains subjective opinions rather than "
                    "objective data points."
                ),
                claims=[],
                total_claims=0,
            )
            await job_store.complete_job(job_id, report)
            return

        total = len(raw_claims)
        await job_store.set_total_claims(job_id, total)
        logger.info(f"Job {job_id}: {total} claims to verify.")

        # ── Steps 3–4: Search + Verify (bounded concurrency) ─────────────
        await job_store.update_status(
            job_id, JobStatus.SEARCHING_WEB, 35,
            f"Searching web for {total} claims...",
        )

        results: List[ClaimResult] = []
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        counter_lock = asyncio.Lock()
        processed = 0

        async def process_claim(raw_claim: dict) -> None:
            nonlocal processed
            async with semaphore:
                # Wait for rate limiter (global throttle)
                await limiter.wait()

                # Web search with filename context (e.g. "TSLA")
                search_results = await search_for_claim(raw_claim["text"], context=filename)
                # Verify claim against retrieved evidence
                claim_result = await verify_claim(raw_claim, search_results)
                results.append(claim_result)

                async with counter_lock:
                    processed += 1
                    current = processed

                progress = 35 + int((current / total) * 55)
                await job_store.update_status(
                    job_id,
                    JobStatus.VERIFYING_CLAIMS,
                    min(progress, 90),
                    f"Verified {current}/{total} claims...",
                    processed_claims=current,
                )

        tasks = [process_claim(claim) for claim in raw_claims]
        await asyncio.gather(*tasks)

        # ── Step 5: Generate report ───────────────────────────────────────
        await job_store.update_status(
            job_id, JobStatus.GENERATING_REPORT, 95, "Generating final report..."
        )

        summary = {v.value: 0 for v in ClaimVerdict}
        for r in results:
            summary[r.verdict.value] += 1

        # Sort: FALSE first, then INACCURATE, UNVERIFIABLE, VERIFIED
        order = {
            ClaimVerdict.FALSE: 0,
            ClaimVerdict.INACCURATE: 1,
            ClaimVerdict.UNVERIFIABLE: 2,
            ClaimVerdict.VERIFIED: 3,
        }
        results.sort(key=lambda r: order.get(r.verdict, 99))

        report = FactCheckReport(
            job_id=job_id,
            filename=filename,
            status=JobStatus.COMPLETED,
            created_at=job_store.get_job(job_id)["created_at"],
            completed_at=datetime.now(timezone.utc),
            summary=summary,
            claims=results,
            total_claims=total,
        )
        await job_store.complete_job(job_id, report)

    except Exception as e:
        user_msg = _friendly_error(e)
        logger.error(f"Pipeline failed for job {job_id}: {e}", exc_info=True)
        await job_store.fail_job(job_id, user_msg)

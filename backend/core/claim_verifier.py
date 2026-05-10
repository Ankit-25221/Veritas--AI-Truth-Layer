import os
import json
import re
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from tenacity import retry, stop_after_attempt
import httpx
from api.models import ClaimResult, ClaimVerdict, ClaimCategory, Evidence
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Model config ──────────────────────────────────────────────────────────────
# gemini-2.0-flash: 1,500 req/day free tier (vs 20/day for gemini-2.5-flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

VERIFICATION_PROMPT = """You are an expert fact-checker. Evaluate the following claim against real web evidence.

Claim: "{claim}"
Category: {category}

Evidence retrieved from the web:
---
{evidence}
---

Based solely on the evidence above, render your verdict:
- VERIFIED: Evidence clearly confirms the claim is accurate
- INACCURATE: Evidence shows the claim has wrong numbers, outdated data, or misleading framing (provide the correct fact)
- FALSE: Evidence directly contradicts the claim (provide the correct fact)
- UNVERIFIABLE: Insufficient or conflicting evidence — cannot confirm or deny

Respond with ONLY valid JSON (no markdown):
{{
  "verdict": "VERIFIED|INACCURATE|FALSE|UNVERIFIABLE",
  "confidence": 0.0,
  "explanation": "One to two sentence explanation citing specific evidence",
  "correction": "The accurate fact if INACCURATE or FALSE, otherwise null"
}}"""


# ── Singleton Gemini client ────────────────────────────────────────────────
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def _format_evidence(search_results: List[Dict[str, Any]]) -> str:
    if not search_results:
        return "No evidence found."
    parts = []
    for i, r in enumerate(search_results[:5], 1):
        title = r.get("title", "Unknown Source")
        url = r.get("url", "")
        snippet = r.get("content", r.get("snippet", ""))[:500]
        parts.append(f"[{i}] {title}\nURL: {url}\n{snippet}")
    return "\n\n".join(parts)


def _build_evidence_objects(
    search_results: List[Dict[str, Any]], verdict_data: Dict[str, Any]
) -> List[Evidence]:
    supports = verdict_data.get("verdict") == "VERIFIED"
    return [
        Evidence(
            source_url=r.get("url", ""),
            source_title=r.get("title", "Unknown"),
            excerpt=r.get("content", r.get("snippet", ""))[:300],
            supports_claim=supports,
        )
        for r in search_results[:4]
    ]


def _parse_retry_after(exc: BaseException) -> float:
    """Extract the retry delay (seconds) advertised in a 429 error body."""
    match = re.search(r"retry in (\d+\.?\d*)s", str(exc), re.IGNORECASE)
    if match:
        return float(match.group(1)) + 2.0  # small safety buffer
    return 45.0  # safe default


def _smart_wait(retry_state: Any) -> float:
    """
    Wait strategy that respects the Gemini API's own retry-after hint on 429s,
    and falls back to short exponential backoff for other transient errors.
    """
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    if exc is None:
        return 2.0
    if isinstance(exc, genai_errors.ClientError) and exc.code == 429:
        delay = _parse_retry_after(exc)
        logger.warning(f"Rate limited by Gemini API — waiting {delay:.0f}s before retry.")
        return delay
    # Exponential for network/other errors: 3s, 6s, 12s
    attempt = retry_state.attempt_number
    return min(3.0 * (2 ** (attempt - 1)), 30.0)


@retry(stop=stop_after_attempt(3), wait=_smart_wait, reraise=True)
async def verify_claim(
    raw_claim: Dict[str, Any], search_results: List[Dict[str, Any]]
) -> ClaimResult:
    """Use Gemini to verify a claim against web search evidence."""
    client = _get_client()
    evidence_text = _format_evidence(search_results)

    prompt = VERIFICATION_PROMPT.format(
        claim=raw_claim.get("text", ""),
        category=raw_claim.get("category", "general"),
        evidence=evidence_text,
    )

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        ),
    )

    raw = response.text
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

    try:
        verdict_data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        verdict_data = json.loads(match.group()) if match else {}

    verdict_str = verdict_data.get("verdict", "UNVERIFIABLE").upper()
    try:
        verdict = ClaimVerdict(verdict_str)
    except ValueError:
        verdict = ClaimVerdict.UNVERIFIABLE

    cat_str = raw_claim.get("category", "general").lower()
    try:
        category = ClaimCategory(cat_str)
    except ValueError:
        category = ClaimCategory.GENERAL

    # Clamp confidence to [0.0, 1.0]
    raw_confidence = verdict_data.get("confidence", 0.5)
    try:
        confidence = max(0.0, min(1.0, float(raw_confidence)))
    except (TypeError, ValueError):
        confidence = 0.5

    return ClaimResult(
        claim_id=str(uuid.uuid4()),
        text=raw_claim.get("text", ""),
        category=category,
        verdict=verdict,
        confidence=confidence,
        evidence=_build_evidence_objects(search_results, verdict_data),
        correction=verdict_data.get("correction") or None,
        explanation=verdict_data.get("explanation", "No explanation provided."),
    )

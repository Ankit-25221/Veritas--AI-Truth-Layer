import os
import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from tenacity import retry, stop_after_attempt
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Model config ──────────────────────────────────────────────────────────────
# gemini-2.0-flash: 1,500 req/day free tier (vs 20/day for gemini-2.5-flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

CLAIM_EXTRACTION_PROMPT = """You are an expert fact-checker analyzing a document for verifiable claims.

Extract the TOP 5 most important, verifiable factual claims from the text below. Do NOT extract more than 5. Focus on:
1. **Total Revenue**
2. **Net Income**
3. **Growth Stats**
4. **Key Delivery/Production numbers**
5. **Major Technical milestones**

EXCLUDE: minor details, opinions, or repetitive stats.

Return ONLY a valid JSON array. No markdown, no explanation, just the JSON:
[
  {{
    "text": "the exact claim verbatim from the text",
    "category": "statistic|date|financial|technical|general",
    "context": "one sentence of surrounding context"
  }}
]

Text to analyze:
---
{text}
---"""


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


def _parse_claims_json(raw: str) -> List[Dict[str, Any]]:
    """Robustly parse JSON from model output."""
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        for key in ("claims", "results", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return []
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        logger.error("Failed to parse claims JSON.")
        return []


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
async def extract_claims(text: str) -> List[Dict[str, Any]]:
    """Use Gemini to extract verifiable claims from document text."""
    client = _get_client()
    prompt = CLAIM_EXTRACTION_PROMPT.format(text=text)

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
    claims = _parse_claims_json(raw)

    # Deduplicate
    seen: set = set()
    unique = []
    for c in claims:
        key = c.get("text", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(c)

    logger.info(f"Extracted {len(unique)} unique claims (model: {GEMINI_MODEL}).")
    return unique

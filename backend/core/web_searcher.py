import os
import asyncio
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.logger import get_logger

logger = get_logger(__name__)


# ── Singleton Tavily client ────────────────────────────────────────────────
_client: Optional[TavilyClient] = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise EnvironmentError("TAVILY_API_KEY environment variable not set.")
        _client = TavilyClient(api_key=api_key)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def search_for_claim(claim_text: str, context: str = "") -> List[Dict[str, Any]]:
    """Search the live web for evidence related to a claim, using context (like company name)."""
    client = _get_client()

    # Extract subject from filename context (e.g. "Tesla" from "TSLA-Q4-...")
    subject = context.split("-")[0].split("_")[0]

    # Neutral query to avoid confirmation bias
    query = f"{subject} {claim_text}" if subject else claim_text

    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            None,
            lambda: client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            ),
        )
        results = response.get("results", [])
        logger.info(f"Found {len(results)} sources for claim: {claim_text[:60]}...")
        return results
    except Exception as e:
        logger.warning(f"Search failed for claim '{claim_text[:60]}': {e}")
        return []

import asyncio
import time
from typing import Optional


class RateLimiter:
    """
    A simple Token Bucket rate limiter to ensure we stay under
    Google Gemini's Free Tier RPM (Requests Per Minute).

    The asyncio.Lock is created lazily on first use to avoid binding it to
    an event loop that doesn't exist at import time.
    """

    def __init__(self, requests_per_minute: int = 10):
        self.delay = 60.0 / requests_per_minute
        self.last_call: float = 0.0
        self._lock: Optional[asyncio.Lock] = None

    @property
    def lock(self) -> asyncio.Lock:
        """Return (or lazily create) the asyncio Lock on the running loop."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def wait(self) -> None:
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.delay:
                wait_time = self.delay - elapsed
                await asyncio.sleep(wait_time)
            self.last_call = time.time()


# Global instance: 10 RPM is the safe limit for most free accounts
limiter = RateLimiter(requests_per_minute=10)

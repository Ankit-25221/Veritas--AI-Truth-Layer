import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from api.models import JobStatus, FactCheckReport
from utils.logger import get_logger

logger = get_logger(__name__)


class JobStore:
    """Thread-safe in-memory job store using asyncio.Lock.

    The Lock is created lazily on first use so it is always bound to the
    running event loop (important for ASGI apps that may import the module
    before starting the loop).
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock: Optional[asyncio.Lock] = None

    @property
    def lock(self) -> asyncio.Lock:
        """Return (or lazily create) the asyncio Lock on the running loop."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def create_job(self, job_id: str, filename: str) -> None:
        async with self.lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "filename": filename,
                "status": JobStatus.QUEUED,
                "progress": 0,
                "message": "Job queued",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "total_claims": None,
                "processed_claims": None,
                "report": None,
                "error": None,
            }
        logger.info(f"Job created: {job_id} | file: {filename}")

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int,
        message: str,
        processed_claims: Optional[int] = None,
    ) -> None:
        async with self.lock:
            if job_id not in self._jobs:
                return
            self._jobs[job_id].update(
                {
                    "status": status,
                    "progress": progress,
                    "message": message,
                    "updated_at": datetime.utcnow(),
                }
            )
            if processed_claims is not None:
                self._jobs[job_id]["processed_claims"] = processed_claims
        logger.info(f"Job {job_id} | {status} | {progress}% | {message}")

    async def set_total_claims(self, job_id: str, total: int) -> None:
        async with self.lock:
            if job_id in self._jobs:
                self._jobs[job_id]["total_claims"] = total

    async def complete_job(self, job_id: str, report: FactCheckReport) -> None:
        async with self.lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(
                    {
                        "status": JobStatus.COMPLETED,
                        "progress": 100,
                        "message": "Fact-check complete!",
                        "updated_at": datetime.utcnow(),
                        "report": report,
                    }
                )
        logger.info(f"Job {job_id} COMPLETED with {report.total_claims} claims.")

    async def fail_job(self, job_id: str, error: str) -> None:
        async with self.lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(
                    {
                        "status": JobStatus.FAILED,
                        "progress": 0,
                        "message": f"Error: {error}",
                        "updated_at": datetime.utcnow(),
                        "error": error,
                    }
                )
        logger.error(f"Job {job_id} FAILED: {error}")

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def get_report(self, job_id: str) -> Optional[FactCheckReport]:
        job = self._jobs.get(job_id)
        if job:
            return job.get("report")
        return None


# Singleton instance
job_store = JobStore()

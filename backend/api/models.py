from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ClaimCategory(str, Enum):
    STATISTIC = "statistic"
    DATE = "date"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    GENERAL = "general"


class ClaimVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    INACCURATE = "INACCURATE"
    FALSE = "FALSE"
    UNVERIFIABLE = "UNVERIFIABLE"


class JobStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING_TEXT = "extracting_text"
    EXTRACTING_CLAIMS = "extracting_claims"
    SEARCHING_WEB = "searching_web"
    VERIFYING_CLAIMS = "verifying_claims"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class Evidence(BaseModel):
    source_url: str
    source_title: str
    excerpt: str
    supports_claim: bool


class ClaimResult(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    category: ClaimCategory
    verdict: ClaimVerdict
    confidence: float
    evidence: List[Evidence]
    correction: Optional[str] = None
    explanation: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    message: str
    created_at: datetime
    updated_at: datetime
    total_claims: Optional[int] = None
    processed_claims: Optional[int] = None


class FactCheckReport(BaseModel):
    job_id: str
    filename: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    summary: dict
    summary_note: Optional[str] = None
    claims: List[ClaimResult]
    total_claims: int


class UploadResponse(BaseModel):
    job_id: str
    message: str
    filename: str

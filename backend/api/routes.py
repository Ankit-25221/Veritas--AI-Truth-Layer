import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from api.models import UploadResponse, JobStatusResponse, FactCheckReport, JobStatus
from utils.job_store import job_store
from core.pipeline import run_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
# Accept both the real PDF MIME type and the browser fallback for binary files
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a PDF and start the async fact-checking pipeline."""
    # Validate by extension (primary guard)
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Validate by MIME type when browser sends a known type
    content_type = (file.content_type or "").split(";")[0].strip()
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{content_type}'. Please upload a PDF file.",
        )

    pdf_bytes = await file.read()

    # Validate file size
    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="File too large. Maximum size is 20 MB."
        )
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    job_id = str(uuid.uuid4())

    # Register job
    await job_store.create_job(job_id, filename)

    # Start pipeline as a background task
    background_tasks.add_task(run_pipeline, job_id, pdf_bytes, filename)

    logger.info(f"New job started: {job_id} | file: {filename}")
    return UploadResponse(
        job_id=job_id,
        message="PDF uploaded. Fact-check pipeline started.",
        filename=filename,
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Poll the current processing status of a job."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        total_claims=job.get("total_claims"),
        processed_claims=job.get("processed_claims"),
    )


@router.get("/report/{job_id}", response_model=FactCheckReport)
async def get_report(job_id: str):
    """Retrieve the completed fact-check report."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job["status"] == JobStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {job.get('error', 'Unknown error')}",
        )

    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=202,
            detail=f"Job is still processing. Status: {job['status']}",
        )

    report = job_store.get_report(job_id)
    if not report:
        raise HTTPException(status_code=500, detail="Report not found despite completion.")

    return report

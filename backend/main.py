# ── Load .env FIRST before any other imports ─────────────────────────────────
# IMPORTANT: load_dotenv() must be called before importing any module that reads
# environment variables at module-level (e.g. GEMINI_MODEL in claim_extractor.py).
# If load_dotenv() runs after those imports, os.getenv() returns None and the
# code falls back to the hardcoded default ("gemini-2.0-flash").
from dotenv import load_dotenv
load_dotenv()

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from utils.logger import get_logger


logger = get_logger(__name__)

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Log startup/shutdown events."""
    logger.info(f"TruthLayer API v{APP_VERSION} starting up…")
    yield
    logger.info("TruthLayer API shutting down.")


app = FastAPI(
    title="TruthLayer Fact-Check API",
    description=(
        "AI-powered automated fact-checking for PDF documents. "
        "Extracts claims, searches the live web, and verifies accuracy."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
]
if frontend_url:
    origins.append(frontend_url)
    origins.append(f"{frontend_url}/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1", tags=["Fact-Check"])


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "service": "TruthLayer Fact-Check API",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "TruthLayer API is running.",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    # reload=True is safe only in development; never enable in production.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "development") == "development",
    )

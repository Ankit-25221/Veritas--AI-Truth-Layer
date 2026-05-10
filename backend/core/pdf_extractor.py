import fitz  # PyMuPDF
from utils.logger import get_logger

logger = get_logger(__name__)

MAX_CHARS = 60_000  # ~15k tokens — safe for Gemini


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract clean text from PDF bytes using PyMuPDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except fitz.FileDataError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {e}") from e

    try:
        pages_text = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                pages_text.append(f"[Page {page_num + 1}]\n{text.strip()}")

        full_text = "\n\n".join(pages_text)

        if not full_text.strip():
            raise ValueError(
                "No text found in PDF. The document may be scanned or image-based."
            )

        # Truncate if too large
        if len(full_text) > MAX_CHARS:
            logger.warning(
                f"PDF text truncated from {len(full_text)} to {MAX_CHARS} chars."
            )
            full_text = full_text[:MAX_CHARS] + "\n\n[... document truncated ...]"

        logger.info(f"Extracted {len(full_text)} chars from {doc.page_count} pages.")
        return full_text

    finally:
        doc.close()

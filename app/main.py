"""FastAPI entry point for DocuFlow AI."""

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from app.config import settings
from app.extractor import DocumentExtractor
from app.schemas import ExtractRequest, ExtractResponse


app = FastAPI(
    title="DocuFlow AI",
    description=(
        "Document extraction MVP using a deterministic mock provider. "
        "It makes no external LLM calls and does not determine legal compliance."
    ),
    version="0.1.0",
)

extractor = DocumentExtractor()


@app.get("/", tags=["General"])
def root() -> dict[str, str]:
    """Return basic API information and links to useful endpoints."""
    return {
        "name": "DocuFlow AI",
        "version": "0.1.0",
        "status": "operational",
        "provider": settings.llm_provider,
        "description": (
            "Document extraction MVP using a deterministic rule-based provider."
        ),
        "docs": "/docs",
        "health": "/health",
        "extract": "/extract",
    }


@app.get("/health", tags=["General"])
def health() -> dict[str, str]:
    """Report the API health and configured extraction provider."""
    return {
        "status": "ok",
        "provider": settings.llm_provider,
    }


@app.post(
    "/extract",
    response_model=ExtractResponse,
    tags=["Extraction"],
)
def extract_document(request: ExtractRequest) -> ExtractResponse:
    """Extract candidate requirements from a document's text."""
    if len(request.text) > settings.max_document_chars:
        raise HTTPException(
            status_code=413,
            detail=(
                "Document exceeds configured limit of "
                f"{settings.max_document_chars} characters."
            ),
        )

    try:
        return extractor.run(request.document_id, request.text)
    except ValidationError as exc:
        # Do not expose internal details or source text in the response.
        raise HTTPException(
            status_code=502,
            detail="Extraction output failed schema validation.",
        ) from exc

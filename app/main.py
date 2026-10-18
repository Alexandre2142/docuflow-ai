"""FastAPI entry point."""
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

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": settings.llm_provider}

@app.post("/extract", response_model=ExtractResponse)
def extract_document(request: ExtractRequest) -> ExtractResponse:
    if len(request.text) > settings.max_document_chars:
        raise HTTPException(
            status_code=413,
            detail=f"Document exceeds configured limit of {settings.max_document_chars} characters.",
        )
    try:
        return extractor.run(request.document_id, request.text)
    except ValidationError as exc:
        # Do not leak internal details or source text in the response.
        raise HTTPException(status_code=502, detail="Extraction output failed schema validation.") from exc

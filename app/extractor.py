"""Application service: provider call followed by deterministic validation."""
from app.llm_client import MockLLMClient
from app.schemas import ExtractResponse
from app.validation import validate_candidates

class DocumentExtractor:
    def __init__(self, client: MockLLMClient | None = None):
        self.client = client or MockLLMClient()

    def run(self, document_id: str, text: str) -> ExtractResponse:
        candidates = self.client.extract(text)
        requirements, warnings = validate_candidates(candidates, text)
        review_required = bool(warnings) or any(
            item.verification_status != "verified" or item.uncertainties
            for item in requirements
        )
        if not requirements:
            warnings.append("No requirement-like sentences were detected by the mock rules.")
            review_required = True
        return ExtractResponse(
            document_id=document_id,
            requirements=requirements,
            review_required=review_required,
            warnings=warnings,
        )

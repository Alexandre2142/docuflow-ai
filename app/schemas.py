
"""Request and response contracts for DocuFlow AI."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RequirementType = Literal[
    "obligation",
    "prohibition",
    "recommendation",
    "uncertain",
]


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(
        default="demo-document",
        min_length=1,
        max_length=120,
    )
    text: str = Field(min_length=1, max_length=50_000)


class Requirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    action: str = Field(min_length=1)
    requirement_type: RequirementType = "uncertain"

    responsible_entity: str | None = None
    deadline: str | None = None
    source_quote: str = Field(min_length=1)

    verification_status: Literal["verified", "needs_review"]
    uncertainties: list[str] = Field(default_factory=list)


class ExtractResponse(BaseModel):
    document_id: str
    requirements: list[Requirement]
    review_required: bool
    provider: Literal["mock"] = "mock"
    warnings: list[str] = Field(default_factory=list)

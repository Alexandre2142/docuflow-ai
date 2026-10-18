
"""Deterministic post-processing and source-quote validation."""

import re
from typing import Any

from app.schemas import Requirement


def normalize_for_match(value: str) -> str:
    """Normalize whitespace and case while preserving punctuation."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def remove_terminal_punctuation(value: str) -> str:
    """Remove terminal sentence punctuation for tolerant quote matching."""
    return re.sub(r"[.!?]+$", "", value).strip()


def validate_candidates(
    candidates: list[dict[str, Any]],
    source_text: str,
) -> tuple[list[Requirement], list[str]]:
    normalized_source = normalize_for_match(source_text)
    comparable_source = remove_terminal_punctuation(normalized_source)

    requirements: list[Requirement] = []
    warnings: list[str] = []

    for index, candidate in enumerate(candidates):
        requirement = Requirement.model_validate(candidate)
        quote = normalize_for_match(requirement.source_quote)
        comparable_quote = remove_terminal_punctuation(quote)

        quote_found = bool(
            quote
            and (
                quote in normalized_source
                or (
                    comparable_quote
                    and comparable_quote in comparable_source
                )
            )
        )

        if not quote_found:
            requirement.verification_status = "needs_review"

            message = "Source quote was not found in the input document."
            if message not in requirement.uncertainties:
                requirement.uncertainties.append(message)

            warnings.append(
                f"Requirement {index} has a source quote "
                "that could not be verified."
            )

        elif requirement.requirement_type == "uncertain":
            requirement.verification_status = "needs_review"

            message = (
                "Requirement classification or applicability "
                "needs human review."
            )
            if message not in requirement.uncertainties:
                requirement.uncertainties.append(message)

        else:
            requirement.verification_status = "verified"

        requirements.append(requirement)

    return requirements, warnings

import pytest
from pydantic import ValidationError
from app.schemas import Requirement
from app.validation import normalize_for_match, validate_candidates

def test_normalize_whitespace_and_case():
    assert normalize_for_match("  The  FACILITY\nshall act. ") == "the facility shall act."

def test_source_quote_is_verified_when_present():
    candidates = [{
        "topic": "Waste management",
        "action": "Maintain records",
        "requirement_type": "obligation",
        "responsible_entity": None,
        "deadline": None,
        "source_quote": "The facility shall maintain records.",
        "verification_status": "needs_review",
        "uncertainties": [],
    }]
    results, warnings = validate_candidates(
        candidates, "THE FACILITY shall maintain records."
    )
    assert results[0].verification_status == "verified"
    assert warnings == []

def test_missing_source_quote_is_flagged():
    candidates = [{
        "topic": "Waste management",
        "action": "Maintain records",
        "responsible_entity": None,
        "deadline": None,
        "source_quote": "The facility shall maintain records.",
        "verification_status": "verified",
        "uncertainties": [],
    }]
    results, warnings = validate_candidates(candidates, "A different source sentence.")
    assert results[0].verification_status == "needs_review"
    assert warnings

def test_requirement_rejects_invalid_status():
    with pytest.raises(ValidationError):
        Requirement(
            topic="Test", action="Do something", source_quote="source",
            verification_status="probably", uncertainties=[]
        )

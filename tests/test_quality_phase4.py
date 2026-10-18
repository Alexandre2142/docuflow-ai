
"""Phase 4 quality tests: uncertainty, review flags, and source fidelity."""

from app.extractor import DocumentExtractor
from app.llm_client import MockLLMClient


def test_reported_requirement_is_marked_uncertain():
    text = "The report states that the operator must notify the authority."

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "uncertain"


def test_uncertain_classification_requires_manual_review_status():
    text = "The report states that the operator must notify the authority."

    response = DocumentExtractor().run("quality-001", text)

    assert len(response.requirements) == 1
    assert response.requirements[0].requirement_type == "uncertain"
    assert response.requirements[0].verification_status == "needs_review"


def test_source_quote_is_preserved_exactly():
    text = (
        "If emissions exceed the permitted limit, "
        "the operator must notify the authority within 24 hours."
    )

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["source_quote"] == text


def test_independent_obligation_is_extracted():
    text = "The operator must record each hazardous waste transfer."

    response = DocumentExtractor().run("quality-002", text)

    assert len(response.requirements) == 1
    assert response.requirements[0].requirement_type == "obligation"
    assert response.requirements[0].source_quote == text


def test_review_flag_is_consistent_with_uncertainty():
    text = "The report states that the operator must notify the authority."

    response = DocumentExtractor().run("quality-003", text)

    assert response.review_required is True
    assert any(
        item.verification_status == "needs_review"
        for item in response.requirements
    )

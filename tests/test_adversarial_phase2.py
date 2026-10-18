
"""Phase 2 adversarial tests: exceptions, scope, and context."""

from app.llm_client import MockLLMClient


def extract(text):
    return MockLLMClient().extract(text)


def test_exception_clause_preserves_the_full_condition():
    text = (
        "The operator must report spills unless the spill "
        "is immediately contained."
    )

    results = extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "obligation"
    assert results[0]["source_quote"] == text


def test_reported_requirement_is_flagged_as_uncertain():
    text = (
        "The report states that the operator must notify the authority."
    )

    results = extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "uncertain"


def test_not_prohibited_is_not_classified_as_a_prohibition():
    text = (
        "The facility is not prohibited from discharging wastewater."
    )

    results = extract(text)

    assert results == []


def test_not_required_is_not_extracted_as_an_obligation():
    text = "The operator is not required to report the spill."

    results = extract(text)

    assert results == []


def test_double_negative_expresses_an_obligation():
    text = (
        "The operator must not fail to notify the authority."
    )

    results = extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "obligation"


def test_semicolon_does_not_silently_drop_a_dependent_clause():
    text = (
        "The operator must report spills; "
        "unless the spill is immediately contained."
    )

    results = extract(text)

    # The full condition should remain attached to the obligation.
    assert len(results) == 1
    assert results[0]["source_quote"] == text
    assert results[0]["requirement_type"] == "obligation"


"""Adversarial tests for the rule-based DocuFlow AI extractor."""

from app.llm_client import MockLLMClient


def test_standard_prohibition_is_classified_correctly():
    text = "The operator must not discharge untreated wastewater."

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "prohibition"


def test_may_not_is_detected_as_a_prohibition():
    text = "The operator may not discharge untreated wastewater."

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "prohibition"


def test_prohibited_from_is_detected_as_a_prohibition():
    text = "The facility is prohibited from discharging untreated wastewater."

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "prohibition"


def test_double_negative_is_not_misclassified_as_a_prohibition():
    text = "The operator shall not fail to report spills."

    results = MockLLMClient().extract(text)

    assert len(results) == 1
    assert results[0]["requirement_type"] == "obligation"


def test_two_requirements_separated_by_semicolon_are_extracted_separately():
    text = (
        "The operator must report spills; "
        "the manager must review the records."
    )

    results = MockLLMClient().extract(text)

    assert len(results) == 2
    assert results[0]["source_quote"] == "The operator must report spills;"
    assert results[1]["source_quote"] == "the manager must review the records."

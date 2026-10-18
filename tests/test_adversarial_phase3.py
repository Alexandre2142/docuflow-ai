
"""Phase 3 adversarial tests: multiple exceptions and grammatical scope."""

from app.llm_client import MockLLMClient


def extract(text):
    return MockLLMClient().extract(text)


def test_exception_attaches_to_the_preceding_requirement():
    text = (
        "The operator must report spills. "
        "The manager must review the records unless the report is incomplete."
    )

    results = extract(text)

    assert len(results) == 2
    assert results[0]["source_quote"] == "The operator must report spills."
    assert results[1]["source_quote"] == (
        "The manager must review the records "
        "unless the report is incomplete."
    )


def test_exception_does_not_attach_to_an_unrelated_previous_requirement():
    text = (
        "The operator must report spills; "
        "the manager must review records; "
        "unless the report is incomplete."
    )

    results = extract(text)

    assert len(results) == 2
    assert results[0]["source_quote"] == "The operator must report spills;"
    assert results[1]["source_quote"] == (
        "the manager must review records; "
        "unless the report is incomplete."
    )


def test_initial_unless_clause_is_not_invented_as_a_requirement():
    text = "Unless the report is incomplete, the manager must review the records."

    results = extract(text)

    assert len(results) == 1
    assert results[0]["source_quote"] == text
    assert results[0]["requirement_type"] == "obligation"


def test_multiple_exceptions_remain_attached_to_their_requirement():
    text = (
        "The operator must report spills unless immediately contained "
        "and except when reporting is legally prohibited."
    )

    results = extract(text)

    assert len(results) == 1
    assert results[0]["source_quote"] == text
    assert results[0]["requirement_type"] == "obligation"


def test_independent_requirements_are_not_merged():
    text = (
        "The operator must report spills; "
        "the manager must review the records."
    )

    results = extract(text)

    assert len(results) == 2
    assert results[0]["source_quote"] == "The operator must report spills;"
    assert results[1]["source_quote"] == "the manager must review the records."

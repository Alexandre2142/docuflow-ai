
from app.llm_client import MockLLMClient


def test_mixed_permission_and_prohibition_are_separated():
    text = (
        "The operator may retain the raw data, "
        "but it must not disclose personal information."
    )

    results = MockLLMClient().extract(text)

    # The optional permission must not be extracted.
    assert len(results) == 1

    requirement = results[0]

    # Only the prohibition should remain.
    assert requirement["requirement_type"] == "prohibition"
    assert "must not disclose personal information" in (
        requirement["source_quote"].lower()
    )

    # The permission must not be mistaken for the requirement.
    assert "may retain the raw data" not in (
        requirement["source_quote"].lower()
    )

"""Deterministic mock extraction. This is NOT an AI model or legal analysis."""

import re
from typing import Any


_ACTION_PATTERN = re.compile(
    r"\b(?:shall|must|should|ought\s+to|"
    r"is\s+(?:not\s+only\s+)?required\s+to|"
    r"are\s+(?:not\s+only\s+)?required\s+to|"
    r"is\s+(?:strongly\s+)?encouraged\s+to|"
    r"are\s+(?:strongly\s+)?encouraged\s+to|"
    r"is\s+recommended\s+to|are\s+recommended\s+to|"
    r"it\s+is\s+recommended\s+that|"
    r"we\s+recommend\s+that|"
    r"may\s+not|is\s+prohibited\s+from|"
    r"are\s+prohibited\s+from)\b",
    re.IGNORECASE,
)

_DENIAL_PATTERN = re.compile(
    r"\b(?:does not|doesn't|do not|don't|did not|didn't)\s+"
    r"(?:state|say|specify|indicate|require)\b",
    re.IGNORECASE,
)

_NOT_ONLY_PATTERN = re.compile(
    r"\bnot only\b.*\bbut also\b",
    re.IGNORECASE,
)

_REPORTED_PATTERN = re.compile(
    r"\b(?:states?|reports?|indicates?|says?)\s+that\b",
    re.IGNORECASE,
)

_DOUBLE_NEGATIVE_PATTERN = re.compile(
    r"\b(?:shall|must|should)\s+not\s+fail\s+to\b",
    re.IGNORECASE,
)

_PROHIBITION_PATTERN = re.compile(
    r"\b(?:must not|shall not|may not|is prohibited from|"
    r"are prohibited from)\b",
    re.IGNORECASE,
)

_RECOMMENDATION_PATTERN = re.compile(
    r"\b(?:should|ought\s+to|is\s+(?:strongly\s+)?encouraged\s+to|"
    r"are\s+(?:strongly\s+)?encouraged\s+to|"
    r"is\s+recommended\s+to|are\s+recommended\s+to|"
    r"it\s+is\s+recommended\s+that|we\s+recommend\s+that)\b",
    re.IGNORECASE,
)

_DEPENDENT_CLAUSE_PATTERN = re.compile(
    r"^(?:unless|except\s+when|provided\s+that|"
    r"subject\s+to)\b",
    re.IGNORECASE,
)

# Split at "but" only when it introduces a separate action clause.
_BUT_ACTION_PATTERN = re.compile(
    r",?\s+\bbut\b\s+(?=[^.!?;]*\b(?:shall|must|should|"
    r"ought\s+to|may\s+not|is\s+required\s+to|are\s+required\s+to|"
    r"is\s+(?:strongly\s+)?encouraged\s+to|"
    r"are\s+(?:strongly\s+)?encouraged\s+to|"
    r"is\s+recommended\s+to|are\s+recommended\s+to|"
    r"is\s+prohibited\s+from|are\s+prohibited\s+from)\b)",
    re.IGNORECASE,
)


class MockLLMClient:
    """Return candidate requirements using simple sentence-level heuristics."""

    def extract(self, text: str) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        parts = re.split(r"(?<=[.!?;])\s+|\n+", text.strip())
        sentences: list[str] = []

        for part in parts:
            quote = part.strip()
            if not quote:
                continue

            # Preserve constructions such as "not only ... but also".
            if sentences and _DEPENDENT_CLAUSE_PATTERN.search(quote):
                sentences[-1] = f"{sentences[-1]} {quote}"
            else:
                sentences.append(quote)

        for sentence in sentences:
            # Keep coordinated clauses together when "but also" is used.
            if _NOT_ONLY_PATTERN.search(sentence):
                clauses = [sentence]
            else:
                clauses = [
                    clause.strip()
                    for clause in _BUT_ACTION_PATTERN.split(sentence)
                    if clause.strip()
                ]

            for quote in clauses:
                if not _ACTION_PATTERN.search(quote):
                    continue

                if (
                    _DENIAL_PATTERN.search(quote)
                    and not _NOT_ONLY_PATTERN.search(quote)
                ):
                    continue

                requirement_type = self._classify(quote)
                uncertainties = [
                    "Mock extraction uses rules, not an AI model.",
                    "Responsible entity and deadline are not inferred by this demo.",
                ]

                if requirement_type == "uncertain":
                    uncertainties.append(
                        "The applicability of the reported requirement is uncertain."
                    )

                candidates.append({
                    "topic": self._topic(quote),
                    "action": quote,
                    "requirement_type": requirement_type,
                    "responsible_entity": None,
                    "deadline": None,
                    "source_quote": quote,
                    "verification_status": "verified",
                    "uncertainties": uncertainties,
                })

        return candidates

    @staticmethod
    def _classify(sentence: str) -> str:
        if _DOUBLE_NEGATIVE_PATTERN.search(sentence):
            return "obligation"

        if _REPORTED_PATTERN.search(sentence):
            return "uncertain"

        if _PROHIBITION_PATTERN.search(sentence):
            return "prohibition"

        if _RECOMMENDATION_PATTERN.search(sentence):
            return "recommendation"

        return "obligation"

    @staticmethod
    def _topic(sentence: str) -> str:
        lowered = sentence.lower()

        if "waste" in lowered:
            return "Waste management"

        if "emission" in lowered:
            return "Emissions"

        if "training" in lowered:
            return "Training"

        return "General requirement"


"""Evaluate DocuFlow against a separate robustness dataset."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.llm_client import MockLLMClient
from app.validation import normalize_for_match


DATASET_PATH = ROOT / "evaluation" / "robustness_dataset.json"


def main() -> int:
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    client = MockLLMClient()

    tp = fp = fn = 0
    classification_correct = classification_total = 0
    citation_hits = citation_total = 0
    errors = []

    for doc in data:
        expected = doc["expected_requirements"]
        predictions = client.extract(doc["text"])

        expected_quotes = Counter(
            normalize_for_match(item["source_quote"])
            for item in expected
        )
        predicted_quotes = Counter(
            normalize_for_match(item["source_quote"])
            for item in predictions
        )

        doc_tp = sum((expected_quotes & predicted_quotes).values())
        doc_fp = sum((predicted_quotes - expected_quotes).values())
        doc_fn = sum((expected_quotes - predicted_quotes).values())

        tp += doc_tp
        fp += doc_fp
        fn += doc_fn

        remaining_expected = list(expected)

        for prediction in predictions:
            quote = normalize_for_match(prediction["source_quote"])
            source = normalize_for_match(doc["text"])

            citation_total += 1
            citation_hits += int(bool(quote) and quote in source)

            match_index = next(
                (
                    i
                    for i, item in enumerate(remaining_expected)
                    if normalize_for_match(item["source_quote"]) == quote
                ),
                None,
            )

            if match_index is not None:
                expected_item = remaining_expected.pop(match_index)
                classification_total += 1

                correct = (
                    prediction["requirement_type"]
                    == expected_item["requirement_type"]
                )
                classification_correct += int(correct)

                if not correct:
                    errors.append(
                        f"{doc['document_id']}: classification mismatch; "
                        f"expected={expected_item['requirement_type']}, "
                        f"predicted={prediction['requirement_type']}; "
                        f"quote={quote!r}"
                    )

        if doc_fp or doc_fn:
            errors.append(
                f"{doc['document_id']}: extraction mismatch; "
                f"TP={doc_tp}, FP={doc_fp}, FN={doc_fn}"
            )

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    classification_accuracy = (
        classification_correct / classification_total
        if classification_total
        else 0.0
    )
    quote_rate = citation_hits / citation_total if citation_total else 0.0

    print("DocuFlow AI - robustness evaluation")
    print(f"Dataset: {DATASET_PATH.name}")
    print(f"Documents: {len(data)}")
    print(f"TP={tp} | FP={fp} | FN={fn}")
    print(f"Extraction precision: {precision:.1%}")
    print(f"Extraction recall: {recall:.1%}")
    print(f"Extraction F1: {f1:.1%}")
    print(
        f"Classification accuracy: {classification_accuracy:.1%} "
        f"({classification_correct}/{classification_total})"
    )
    print(
        f"Source quote match rate: {quote_rate:.1%} "
        f"({citation_hits}/{citation_total})"
    )

    print("\nDiagnostic findings:")
    if errors:
        for error in errors:
            print(f"- {error}")
    else:
        print("- No extraction or classification mismatches detected.")

    print(
        "\nCaveat: this is a small, manually annotated diagnostic set. "
        "Results do not establish generalization to real regulatory documents."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Synthetic evaluation set

`dataset.json` contains 15 synthetic English documents with manually annotated requirement sentences.

Run from the repository root:

```powershell
python scripts/evaluate.py
```

The evaluator reports TP, FP, FN, precision, recall, F1 and source-quote match rate. Matching is case-insensitive, whitespace-normalized and multiset-aware so repeated sentences are handled without overcounting.

Limitations: this small dataset is not representative of real regulatory documents. Labels reflect the MVP's narrow sentence-level definition, not legal interpretation. Quote match rate checks literal presence only, not semantic correctness. The mock copies source sentences as quotes, so this metric is expected to be high by construction.

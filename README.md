# DocuFlow AI

**Document Intelligence & Structured Extraction — MVP 0.1.0**

DocuFlow AI is a small FastAPI service that identifies requirement-like statements in plain-text documents and returns structured records with source quotations.

The project demonstrates a document-processing pipeline with API validation, structured outputs, deterministic extraction, source-quote verification, automated testing, and evaluation benchmarks.

> **Important:** The current provider is a deterministic, rule-based mock. It does not call an LLM, perform semantic AI extraction, or determine legal compliance. The project validates the application architecture and evaluation workflow before a real AI provider is integrated.

## Features

- `POST /extract` accepts a document ID and plain text.
- Pydantic models define and validate request and response contracts.
- A deterministic rule-based extractor identifies candidate requirements using linguistic patterns such as `shall`, `must`, `should`, and `is required to`.
- Requirement-like statements are classified as obligations, prohibitions, recommendations, or uncertain cases.
- Source quotations are checked against the input document using case-insensitive whitespace normalization.
- Missing or uncertain quotations and classifications can trigger human review.
- `GET /health` reports service status and the configured provider.
- Automated tests cover the API, schema validation, extraction rules, adversarial cases, and source-quote verification.
- Separate synthetic evaluation datasets measure extraction and classification performance.
- No API key or external service is required.

## Architecture

```text
HTTP request
    |
    v
FastAPI request validation
    |
    v
Deterministic mock extractor
    |
    v
Structured candidate requirements
    |
    v
Pydantic schema validation
    |
    v
Source-quote verification
    |
    v
Structured JSON response
```

The provider implementation is isolated in `app/llm_client.py`.

The surrounding application separates extraction, schema validation, and post-processing. A future LLM adapter should preserve these contracts and must not bypass validation, source checking, error handling, or human-review flags.

## Requirements

- Python 3.11 or newer is the documented target; compatibility should be verified against the installed dependencies.
- `pip`
- A virtual environment is recommended.

The project has been tested in a development environment using Python 3.14.7.

## Run locally

Clone the repository and navigate to its root directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

- Swagger UI: <http://127.0.0.1:8000/docs>
- Health endpoint: <http://127.0.0.1:8000/health>

## Example request

Send a document to `POST /extract`.

```json
{
  "document_id": "demo-001",
  "text": "The facility shall maintain a record of each hazardous waste transfer."
}
```

Example command using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "demo-001",
    "text": "The facility shall maintain a record of each hazardous waste transfer."
  }'
```

On Windows PowerShell, the request can also be submitted through Swagger UI at `/docs`.

The exact response structure is defined by the application's Pydantic schemas. The extracted content is a candidate interpretation, not a legal determination.

## Run tests

Run the complete test suite from the repository root:

```powershell
python -m pytest -v
```

The latest recorded run passed **33 tests**, with one Starlette deprecation warning related to `httpx` and `starlette.testclient`.

The suite covers:

- API request and response behavior.
- Invalid and empty input handling.
- Requirement classification.
- Negation and double-negation cases.
- Multiple requirements in one passage.
- Exceptions and dependent clauses.
- Reported requirements and uncertainty.
- Source-quote validation.
- Mixed permissions and prohibitions.

Test results describe the tested code and environment. Rerun the suite after making changes to verify the current state.

## Configuration

The project includes an `.env.example` file for documenting local settings.

Copy it to `.env` if you want to keep local configuration values in one place. The application does not automatically load `.env`; environment variables must be exported or loaded separately.

Supported settings:

| Variable | Value or default | Purpose |
|---|---|---|
| `DOCUFLOW_LLM_PROVIDER` | `mock` | Selects the only provider currently supported |
| `DOCUFLOW_MAX_DOCUMENT_CHARS` | `50000` | Maximum document length accepted by the endpoint |

No API credentials are required for the current implementation.

Do not commit `.env` files, API keys, tokens, or other secrets.

## Response semantics

### Requirement classification

The mock supports four requirement types:

- `obligation`
- `prohibition`
- `recommendation`
- `uncertain`

Classification relies on deterministic linguistic patterns. It is not a complete interpretation of natural language or regulatory context.

### Source verification

`verification_status="verified"` means that the source quotation was found in the input after the configured normalization.

It does **not** prove that:

- The quotation was interpreted correctly.
- The extracted statement is legally binding.
- The classification is semantically correct.
- The requirement applies to a particular organization.
- The document is complete or authoritative.

A missing quotation is marked `needs_review`.

Uncertain classifications are also intended to require human review.

### Review flags

`review_required=true` indicates that the extraction needs human attention under the application's current review rules.

The mock includes explicit uncertainty notes because it uses heuristic rules and does not perform full semantic interpretation.

### Responsible entity and deadline

The current mock deliberately does not infer these fields. `responsible_entity` and `deadline` remain `null`.

### No matching requirements

If no requirement-like statements are detected, the response contains an empty `requirements` array and a warning.

An empty result does not prove that a document contains no applicable requirements.

## Synthetic evaluation

The repository includes a manually annotated synthetic dataset in `evaluation/dataset.json`.

Run the benchmark from the repository root:

```powershell
python scripts/evaluate.py
```

The script reports:

- True positives (TP).
- False positives (FP).
- False negatives (FN).
- Extraction precision, recall, and F1.
- Classification accuracy on matched source quotations.
- Source-quote match rate.
- Per-document extraction counts.

The latest recorded run reported:

| Metric | Result |
|---|---:|
| Documents | 25 |
| True positives | 21 |
| False positives | 0 |
| False negatives | 0 |
| Extraction precision | 100% |
| Extraction recall | 100% |
| Extraction F1 | 100% |
| Classification accuracy | 100% (21/21) |
| Source-quote match rate | 100% (21/21) |

These results apply only to the included synthetic dataset and the deterministic mock. They do not establish real-world extraction performance or legal accuracy.

## Robustness evaluation

A separate diagnostic dataset is available in `evaluation/robustness_dataset.json`.

Run it with:

```powershell
python scripts/evaluate_robustness.py
```

The dataset contains 10 manually annotated synthetic documents covering cases such as:

- Optional permissions.
- Negation and double negation.
- Exceptions.
- Recommendations.
- Deadlines.
- Reported requirements.
- Multiple actors.
- Mixed permissions and prohibitions.

The latest recorded run reported:

| Metric | Result |
|---|---:|
| Documents | 10 |
| True positives | 9 |
| False positives | 0 |
| False negatives | 0 |
| Extraction precision | 100% |
| Extraction recall | 100% |
| Extraction F1 | 100% |
| Classification accuracy | 100% (9/9) |
| Source-quote match rate | 100% (9/9) |

The mixed-modality regression case is covered by `tests/test_adversarial_phase5.py`.

These figures are a snapshot of the latest reported run. Rerun the benchmark after changing the extractor or evaluation data.

**Evaluation limitation:** this is a small, manually annotated diagnostic set. Its results do not establish generalization to unseen real-world regulatory documents. The evaluation is not an independent legal-quality assessment, and the mock is not an LLM.

## Current limitations

- The extractor is deterministic and rule-based, not an AI model.
- English-language heuristic patterns only.
- Plain-text input only; no PDF, OCR, tables, or multi-document ingestion.
- Sentence and clause segmentation is intentionally simple and can fail on complex punctuation or language constructions.
- Topic classification is keyword-based.
- Responsible entities and deadlines are not inferred.
- Quote verification uses normalized substring matching. It can reject legitimate paraphrases and cannot establish semantic entailment.
- No authentication, persistence, rate limiting, or production deployment hardening.
- No guarantee of legal accuracy, completeness, or applicability.
- The included evaluation datasets are small and synthetic.

The application is a prototype for exploring structured document extraction, validation, and evaluation—not a production legal-compliance system.

## Suggested next increments

1. Expand the manually annotated robustness dataset with additional independent examples.
2. Evaluate performance on documents not used to design the extraction rules.
3. Improve clause segmentation while preserving existing regression tests.
4. Introduce a real LLM provider behind the existing provider boundary.
5. Add explicit provider timeouts, error handling, and bounded retries.
6. Evaluate structured extraction and source attribution separately from semantic correctness.
7. Add PDF ingestion and OCR only after the plain-text pipeline has been evaluated adequately.
8. Add authentication, persistence, rate limiting, and deployment hardening before production use.

## License

No license has been selected yet. Choose a license before publishing the repository publicly. Without an explicit license, others generally do not receive permission to reuse, modify, or redistribute the code beyond applicable legal exceptions.

## Project status

**MVP 0.1.0 — deterministic prototype**

DocuFlow AI currently demonstrates a testable FastAPI document-processing pipeline, structured output validation, source-quote checking, and a repeatable synthetic evaluation workflow.

The next major milestone is to integrate and evaluate a real AI provider while retaining the current validation and review safeguards.
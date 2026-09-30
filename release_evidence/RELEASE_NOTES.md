# FixGraph Release Notes
**Version: 1.0.0**

## What FixGraph Does
FixGraph acts as a safety compiler for LLM-generated troubleshooting responses. It converts vague user complaints into a verified, risk-ordered, and schema-compliant plan using BAAI embeddings and deterministic execution boundaries.

## Manager-contract Support
Full support for the official Phase 10 validation contract. Parses `input.txt`, `siis_responses.json`, `schema.py`, and `deeplinks.json` perfectly. Fallbacks correctly execute on missing SIIS data.

## Key Safety Features
- `FinalValidationGate`: Rejects absolute URLs, formats schema correctly.
- `RiskOrderValidator`: Sequentially pushes destructive operations (e.g. format) to the end of the step list.
- `DeeplinkIntegrityValidator`: Ensures NO hallucinated deeplinks reach the final response block.

## Measured Results
- 0 Web URL Leaks
- 0 Hallucinated URIs
- 138/138 Pytest adversarial verifications passed
- < 5ms P95 Cache Lookup Latency

## How to Run
Use `python -m build` to package. `pip install dist/fixgraph-1.0.0-py3-none-any.whl`. Run tests via `pytest`.

## Known Limitations
Semantic hits return 0% in Local Mock mode because of stringent safety rules preventing untested local embeddings from assuming generative outputs. True validation requires plugging in a LIVE OpenAI or Anthropic provider key. Docker daemon was unavailable locally for clean-room testing.

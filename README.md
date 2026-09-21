# FixGraph — Smart Guided Troubleshooting Engine

**Samsung PRISM GenAI Hackathon 3.0 (Theme 2)**  
*Release Tag: `PRISM_GENAI_HACKATHON_Y2026`*

FixGraph is a **verified troubleshooting compiler** for Samsung Galaxy device complaints. It converts vague, multi-symptom complaints into a schema-valid, evidence-grounded, risk-ordered troubleshooting plan whose actionable steps map to exact catalog-approved masked Settings deeplinks.

---

## Key Features

1. **Deterministic Deeplink Retrieval**: Hybrid (BM25 + Dense vector similarity) indexing over descriptive catalog metadata without matching against masked URI tokens. Exact URI strings are preserved verbatim.
2. **Strict URL & Text Hygiene**: 0% web URL leakage (`http`, `https`, `www`, markdown web links). Programmatic enforcement of Goal syntax, 2-3 word sentence case title, and 5-7 word `It will...` description.
3. **One Action = One Physical Screen**: Cross-screen candidate steps are grouped or split so each action represents exactly one physical Settings screen or feature.
4. **Risk-Aware Sequencing**: Interventions are classified into risk tiers (`auto` standard configuration, `critical` disruptive/reset operations, `manual` physical interventions). Critical actions are sequenced last.
5. **Two-Stage Persistent Semantic Cache**: Fast-path SQLite cache pairing canonical case signature matching with vector similarity. Achieves **>=80% paraphrase hit rate** with **P95 latency <=300ms**.

---

## Quick Start & Installation

### Requirements
- Python 3.11+
- Pip / Setuptools

### Setup Instructions

```bash
# Clone the repository and navigate into directory
cd Samsung_PRISM_Theme2_FixGraph_Execution_Pack

# Install package in editable mode
pip install -e .

# Run test suite
python -m pytest

# Run API server
uvicorn fixgraph.app:app --reload --port 8000
```

### Endpoints
- **Troubleshoot**: `POST /v1/troubleshoot`
- **Health Check**: `GET /health`

---

## Submission & Verification Commands

```bash
# Run unit, integration, schema & adversarial tests
python -m pytest tests/

# Run benchmark suites
python scripts/benchmark_cache.py
python scripts/benchmark_retrieval.py
python scripts/benchmark_latency.py
```

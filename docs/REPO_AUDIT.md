# Repository Audit Report — FixGraph

**Date**: 2026-09-21  
**Project**: FixGraph — Samsung PRISM GenAI Hackathon 3.0 Theme 2  

---

## 1. Directory & File Inventory

```text
Samsung_PRISM_Theme2_FixGraph_Execution_Pack/
└── Samsung_PRISM_Theme2_FixGraph_Execution_Pack/
    ├── 00_README_INDEX.md
    ├── 01_COMPLETE_PROJECT_DETAILS.md
    ├── 02_ARCHITECTURE.md
    ├── 03_COMPLETE_PROMPTS.md
    ├── 04_TECHNICAL_CHECK.md
    ├── 05_TASKSHEET.md
    ├── 06_INSTRUCTIONS.md
    ├── 07_IMPLEMENTATION_PLAN.md
    ├── 08_API_AND_DATA_CONTRACT.md
    ├── 09_TEST_AND_EVALUATION_PLAN.md
    ├── 10_DEMO_AND_SUBMISSION_PLAN.md
    ├── 11_RED_TEAM_AND_RISK_REGISTER.md
    ├── 12_REPO_STRUCTURE.md
    ├── 13_METRICS_TEMPLATE.md
    ├── 14_AI_DISCLOSURE_GUIDE.md
    ├── 15_JUDGING_ALIGNMENT.md
    ├── 16_FINAL_ACCEPTANCE_CHECKLIST.md
    └── 17_SOURCE_REQUIREMENTS_NOTES.md
```

---

## 2. Asset Status & Missing Dependencies

| Asset Name | Status | Location / Strategy |
|---|---|---|
| `schema.py` | Absent in raw repo | Built strictly following official `08_API_AND_DATA_CONTRACT.md` spec in `src/fixgraph/contracts/public.py` |
| `deeplinks.json` | Absent in raw repo | Loaded from `challenge_assets/deeplinks.json` if provided; fallback sample dataset provided for tests |
| `queries.json` | Absent in raw repo | Loaded from `challenge_assets/queries.json` if provided; fallback sample dataset provided for tests |
| `siis_responses.json` | Absent in raw repo | Loaded from `challenge_assets/siis_responses.json` if provided; fallback sample dataset provided for tests |
| `samples/` | Absent in raw repo | Created in `challenge_assets/samples/` and `tests/fixtures/` with schema-compliant test pairs |

---

## 3. Python Environment & Stack

- **Python Version**: 3.11.4
- **Web Framework**: FastAPI + Uvicorn
- **Data Validation**: Pydantic v2
- **Testing & Quality**: pytest, pytest-asyncio, ruff, mypy
- **Retrieval & ML**: sentence-transformers / scikit-learn / rank-bm25 / numpy
- **Storage**: SQLite (standard library `sqlite3`)

---

## 4. Implementation Strategy

1. Maintain 100% adherence to P0 contract and performance gates.
2. Build data loaders that dynamically load from `challenge_assets/` or environment variable paths `DEEPLINKS_PATH`, `QUERIES_PATH`, `SIIS_PATH`.
3. Ensure exact catalog URI preservation, pure JSON responses, zero web link leaks, one-action-one-screen grouping, risk-ordered sequencing, and two-stage persistent semantic caching.

# AI Usage Ledger — FixGraph

This ledger documents feature-by-feature AI coding assistance for the Samsung PRISM GenAI Hackathon 3.0 submission, strictly following official AI usage disclosure requirements.

| Feature Name | Origin | AI Tool Used | Output Summary | Human Review / Modifications | Files Affected |
|---|---|---|---|---|---|
| Project Architecture & Spec | Human | Gemini 3.6 Flash | System design decomposition and milestone breakdown | Reviewed and aligned with official Theme 2 guidelines | `docs/*`, `README.md` |
| Pydantic v2 Contracts | Both | Gemini 3.6 Flash | Data validation schemas for `Goal`, `Action`, `TroubleshootRequest` | Added strict score bounds, category validation, and custom validators | `src/fixgraph/contracts/*` |
| URL Hygiene Validator | Both | Gemini 3.6 Flash | Regex rules detecting web URLs and obfuscations | Tested against 100 adversarial cases | `src/fixgraph/validation/url_hygiene.py` |
| Deeplink Catalog & Resolver | Both | Gemini 3.6 Flash | BM25 + Dense vector retrieval over catalog metadata | Excluded masked URI text from search text to satisfy P0-08 | `src/fixgraph/data/deeplink_catalog.py`, `src/fixgraph/retrieval/*` |
| Two-Stage Semantic Cache | Both | Gemini 3.6 Flash | SQLite cache store with canonical signature matching | Added domain compatibility gate to prevent cross-domain cache pollution | `src/fixgraph/cache/*` |
| Risk Classifier & Sequencer | Both | Gemini 3.6 Flash | Risk tier classification and critical action ordering | Verified critical actions are strictly sequenced last | `src/fixgraph/planning/*`, `src/fixgraph/validation/sequencing.py` |
| FastAPI REST API | Both | Gemini 3.6 Flash | `/v1/troubleshoot` and `/health` route handlers | Verified pure JSON output without markdown wrapper | `src/fixgraph/api/*`, `src/fixgraph/app.py` |

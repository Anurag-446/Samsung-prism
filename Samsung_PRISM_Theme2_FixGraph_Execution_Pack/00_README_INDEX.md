# FixGraph — Samsung PRISM GenAI Hackathon 3.0 Theme 2 Execution Pack

This folder is a complete implementation and submission playbook for **Theme 2: Smart Guided Troubleshooting Engine**. The proposed project name is **FixGraph**.

## What FixGraph is

FixGraph is a **verified troubleshooting compiler** for Galaxy-device complaints. It converts vague, colloquial, sometimes multi-symptom complaints into a schema-valid, evidence-grounded, risk-ordered troubleshooting plan whose actionable steps map to exact, catalog-approved masked Settings deeplinks.

The design deliberately separates **generative reasoning** from **deterministic safety/contract enforcement**:

1. Normalize complaint and extract symptom atoms.
2. Retrieve only relevant SIIS/reference evidence.
3. Generate or parse candidate actions.
4. Resolve each action to a specific target screen using hybrid retrieval over deeplink metadata.
5. Group steps by physical screen: **one action = one screen**.
6. Order actions from least disruptive to critical/destructive.
7. Validate against the supplied schema and rule gates.
8. Scrub all forbidden web URLs.
9. Use only deeplinks copied verbatim from the supplied catalog.
10. Cache the validated plan by semantic case signature for fast paraphrase reuse.

## Source requirements this pack is designed around

The supplied Theme 2 guide specifies, among other constraints:

- Endpoint: `POST /v1/troubleshoot`.
- Health endpoint: `GET /health`.
- Strict schema conformance.
- No web URLs in output.
- No hallucinated troubleshooting steps outside supplied reference evidence.
- Deeplinks must come verbatim from the supplied deeplink catalog.
- Do not match against masked URI strings; retrieve using descriptive metadata.
- One action should represent one physical Settings screen/feature.
- Critical/destructive operations must come last.
- Semantic paraphrase cache target: **>=80% hit rate on unseen paraphrases**.
- Cached fast-path target: **P95 <=300 ms**.
- Cold-path target: **P95 <=8 s**.
- Deterministic behavior for semantically identical inputs.
- Pure JSON API responses; no markdown fences or conversational preamble.

The overall hackathon submission rubric in the supplied brief is:

- Working prototype & functionality: **30%**
- Technical depth & feasibility: **25%**
- Innovation & originality: **20%**
- Relevance to theme: **15%**
- Presentation & documentation: **10%**

Final submission deadline in the supplied brief: **25 September 2026, 11:59 PM**. The final judged Git commit must carry the release tag **`PRISM_GENAI_HACKATHON_Y2026`**.

## Files in this pack

| File | Purpose |
|---|---|
| `01_COMPLETE_PROJECT_DETAILS.md` | Product concept, requirements, novelty, scope and success criteria |
| `02_ARCHITECTURE.md` | End-to-end technical architecture, components, flows and design decisions |
| `03_COMPLETE_PROMPTS.md` | Sequential coding-agent prompts from repo initialization to final audit |
| `04_TECHNICAL_CHECK.md` | P0/P1/P2 technical verification gates and pass/fail checklist |
| `05_TASKSHEET.md` | Execution backlog with owners, dependencies, status and DoD |
| `06_INSTRUCTIONS.md` | Operating rules for developers and AI coding agents |
| `07_IMPLEMENTATION_PLAN.md` | Phase-by-phase build plan and deadline plan |
| `08_API_AND_DATA_CONTRACT.md` | API contract, schemas, internal types and validation strategy |
| `09_TEST_AND_EVALUATION_PLAN.md` | Unit, integration, adversarial, latency, cache and ablation tests |
| `10_DEMO_AND_SUBMISSION_PLAN.md` | 5-minute demo, PPT mapping, README and final submission checklist |
| `11_RED_TEAM_AND_RISK_REGISTER.md` | Failure modes, adversarial tests and mitigations |
| `12_REPO_STRUCTURE.md` | Proposed repository tree and responsibility of each module |
| `13_METRICS_TEMPLATE.md` | Ready-to-fill benchmark/report template |
| `14_AI_DISCLOSURE_GUIDE.md` | How to maintain the supplied AI usage disclosure evidence |
| `15_JUDGING_ALIGNMENT.md` | Maps technical work to the official scoring rubric without sacrificing correctness |
| `16_FINAL_ACCEPTANCE_CHECKLIST.md` | Single final go/no-go checklist before tagging and submission |

## Recommended implementation stack

A laptop-friendly baseline:

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2
- `sentence-transformers` small embedding model
- BM25 (`rank-bm25`) + dense cosine similarity
- FAISS or NumPy for small local indexes
- SQLite for persistent semantic cache and run metadata
- Optional Redis only if already available; do **not** make it a hard dependency
- LLM provider behind an interface; use strict structured output where supported
- `pytest`, `pytest-asyncio`, `hypothesis`
- `ruff`, `mypy`
- Docker

## Recommended development principle

**Never let the LLM directly emit a trusted deeplink or trusted final response.** The LLM may propose intent, symptoms, actions, or search text, but the application layer must resolve exact deeplinks from the local catalog and must validate every output deterministically.

## Start here

1. Read `01_COMPLETE_PROJECT_DETAILS.md`.
2. Adopt `12_REPO_STRUCTURE.md`.
3. Give your coding agent Prompt 00 from `03_COMPLETE_PROMPTS.md`.
4. Execute `05_TASKSHEET.md` in dependency order.
5. Run `04_TECHNICAL_CHECK.md` after every phase.
6. Before submission, complete `16_FINAL_ACCEPTANCE_CHECKLIST.md` and tag the exact judged commit.

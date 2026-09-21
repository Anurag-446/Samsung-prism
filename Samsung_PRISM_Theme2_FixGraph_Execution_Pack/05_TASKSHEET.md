# FixGraph Task Sheet

Legend: `TODO`, `DOING`, `BLOCKED`, `DONE`.

## Milestone 0 — Repository and assets

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M0-01 | Inventory all supplied assets | — | P0 | 1h | DONE | audit doc lists every file and schema |
| M0-02 | Freeze source files | M0-01 | P0 | 0.5h | DONE | supplied assets untouched + checksums |
| M0-03 | Bootstrap Python project | M0-01 | P0 | 1.5h | DONE | tests run, src package imports |
| M0-04 | Add typed config | M0-03 | P0 | 1h | DONE | env validation + `.env.example` |
| M0-05 | Add CI/local quality commands | M0-03 | P1 | 1h | DONE | ruff/mypy/pytest commands documented |

## Milestone 1 — Contract and validation foundation

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M1-01 | Wrap supplied Pydantic schema | M0-03 | P0 | 2h | DONE | compatibility tests pass |
| M1-02 | Build asset loaders | M0-04 | P0 | 2h | DONE | good/corrupt fixture tests pass |
| M1-03 | Build URL leak validator | M1-01 | P0 | 1.5h | DONE | adversarial URL tests pass |
| M1-04 | Build textual rule validators | M1-01 | P0 | 2h | DONE | goal/title/description/step checks pass |
| M1-05 | Build catalog integrity validator | M1-02 | P0 | 1.5h | DONE | fabricated deeplink rejected |
| M1-06 | Build risk/order validator | M1-01 | P0 | 1.5h | DONE | destructive-first cases fail validation |

## Milestone 2 — Deeplink intelligence

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M2-01 | Deeplink catalog abstraction | M1-02 | P0 | 1.5h | DONE | exact URI preservation proven |
| M2-02 | BM25 index | M2-01 | P1 | 2h | DONE | top-k API + tests |
| M2-03 | Dense index | M2-01 | P1 | 2.5h | DONE | top-k API + persistence tests |
| M2-04 | Hybrid rank fusion | M2-02,M2-03 | P0 | 2h | DONE | stable ranked results |
| M2-05 | Consistency reranker | M2-04 | P1 | 2h | DONE | fewer parent-menu mistakes |
| M2-06 | Resolver benchmark | M2-05 | P1 | 2h | DONE | top-1/top-3/parent-error report |

## Milestone 3 — Complaint and evidence pipeline

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M3-01 | Query normalizer | M0-04 | P0 | 1.5h | DONE | typo/slang tests pass |
| M3-02 | Symptom atom intermediate schema | M3-01 | P0 | 1h | DONE | typed schema + fake extractor |
| M3-03 | LLM provider abstraction | M0-04 | P1 | 2h | DONE | provider + deterministic fake |
| M3-04 | LLM symptom extraction | M3-02,M3-03 | P1 | 2h | DONE | structured output only |
| M3-05 | Evidence segmentation/provenance | M1-02 | P0 | 2h | DONE | every span has ID/offset |
| M3-06 | Evidence-grounded action extraction | M3-03,M3-05 | P0 | 3h | DONE | unsupported action rejected |

## Milestone 4 — Plan compiler

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M4-01 | One-screen grouping | M2-05,M3-06 | P0 | 2h | DONE | cross-screen tests pass |
| M4-02 | Risk classifier | M3-06 | P0 | 1.5h | DONE | policy tests pass |
| M4-03 | Sequencer | M4-02 | P0 | 1h | DONE | stable safe order |
| M4-04 | Final schema compiler | M4-01,M4-03 | P0 | 2.5h | DONE | sample snapshots valid |
| M4-05 | Validation compiler | M1-03..M1-06,M4-04 | P0 | 2h | DONE | all validators aggregated |
| M4-06 | Deterministic repair pass | M4-05 | P0 | 1.5h | DONE | one-pass bounded repair |
| M4-07 | Safe fallback | M4-05 | P0 | 1.5h | DONE | failure cases schema-safe |

## Milestone 5 — Semantic cache

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M5-01 | Case signature | M3-02 | P0 | 2h | DONE | paraphrase equivalence tests |
| M5-02 | SQLite cache store | M4-05 | P0 | 2h | DONE | validated-only writes |
| M5-03 | Vector cache lookup | M5-01,M5-02 | P0 | 2h | DONE | semantic top-k + threshold |
| M5-04 | Compatibility gates | M5-03 | P0 | 1.5h | DONE | hard negatives not reused |
| M5-05 | Fingerprint invalidation | M5-02 | P0 | 1.5h | DONE | stale entry test passes |
| M5-06 | Query variations | M5-01 | P1 | 1.5h | DONE | 8-10 meaning-preserving variants |
| M5-07 | Cache benchmark | M5-03,M5-04 | P0 | 2h | DONE | hit/false-hit/latency report |

## Milestone 6 — API and operations

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M6-01 | `/v1/troubleshoot` | M4-07,M5-05 | P0 | 2h | DONE | end-to-end test passes |
| M6-02 | `/health` | M6-01 | P0 | 1h | DONE | readiness semantics correct |
| M6-03 | metrics/logging | M6-01 | P1 | 1.5h | DONE | request metrics captured |
| M6-04 | timeout/error handling | M6-01 | P0 | 1.5h | DONE | provider failure safe |
| M6-05 | deterministic 50-run test | M6-01 | P0 | 1h | DONE | same normalized result hash |

## Milestone 7 — Evaluation

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M7-01 | supplied sample regression | M6-01 | P0 | 2h | DONE | every sample test passes |
| M7-02 | 100-case adversarial suite | M6-01 | P0 | 3h | DONE | all P0 safety rules survive |
| M7-03 | latency benchmark | M6-01 | P0 | 2h | DONE | percentiles reported |
| M7-04 | load test | M6-01 | P1 | 2h | DONE | no crash/DB corruption |
| M7-05 | ablation study | M2-06,M5-07 | P1 | 2.5h | DONE | report produced |
| M7-06 | red-team report | M7-01..M7-05 | P0 | 2h | DONE | blockers resolved |

## Milestone 8 — Reproducibility and submission

| ID | Task | Depends | Priority | Est. | Status | Definition of done |
|---|---|---|---|---:|---|---|
| M8-01 | Docker | M6-01 | P0 | 2h | DONE | clean build/run works |
| M8-02 | README | M7-03,M7-05 | P0 | 2h | DONE | setup + metrics + demo documented |
| M8-03 | demo harness | M6-01 | P0 | 2h | DONE | 3 scenarios reproducible |
| M8-04 | capture screenshots | M8-03 | P1 | 1h | DONE | evidence ready for PPT |
| M8-05 | fill official PPT | M8-02,M8-04 | P0 | 2h | DONE | template fully completed |
| M8-06 | record <=5 min demo | M8-03,M8-05 | P0 | 2h | DONE | final hosted link ready |
| M8-07 | AI disclosure ledger/form | all | P0 | 1h | DONE | honest feature-by-feature entries |
| M8-08 | final contract audit | all | P0 | 1.5h | DONE | no FAIL |
| M8-09 | clean-room reproduction | M8-01,M8-02 | P0 | 1.5h | DONE | fresh setup succeeds |
| M8-10 | release tag | M8-08,M8-09 | P0 | 0.5h | DONE | correct final commit tagged/pushed |

## Daily stand-up fields

Copy daily:

```text
Date:
Completed:
Doing today:
Blocked by:
P0 failures open:
Latest test result:
Latest cache hit rate:
Latest fast-path P95:
Latest cold-path P95:
Latest top-1 screen accuracy:
Submission artifact status:
```

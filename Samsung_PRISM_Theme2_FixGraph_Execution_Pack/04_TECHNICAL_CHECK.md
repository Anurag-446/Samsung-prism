# Technical Check — FixGraph Release Gates

Use this as a red/green checklist. **P0 failures block submission.**

## A. P0 contract gates

| ID | Check | Pass condition | Suggested test |
|---|---|---|---|
| P0-01 | API path | `POST /v1/troubleshoot` works | API integration test |
| P0-02 | Health path | `GET /health` readiness behavior correct | startup/health test |
| P0-03 | Schema | 100% outputs validate against supplied contract | `pytest -k schema` |
| P0-04 | Pure JSON | no markdown fence/preamble/suffix | response content-type + parser test |
| P0-05 | URL leak | zero `http`, `https`, `www`, markdown web links in visible plan text | adversarial URL suite |
| P0-06 | Catalog integrity | every actionable deeplink exists exactly in provided catalog | catalog integrity test |
| P0-07 | No synthesized URI | no code/model creates `bixby://` strings | static grep + unit test |
| P0-08 | Retrieval field hygiene | masked URI excluded from semantic index text | index snapshot test |
| P0-09 | Evidence grounding | every semantic action backed by source evidence | provenance test |
| P0-10 | No hallucinated fallback | insufficient evidence -> empty/safe fallback | no-context test |
| P0-11 | One action = one screen | cross-screen steps are split | action granularity tests |
| P0-12 | Manual action deeplink | manual actions carry no actionable deeplink | category test |
| P0-13 | Critical order | critical/destructive actions last where required | sequencing suite |
| P0-14 | Score range | all scores in [0,1] | property test |
| P0-15 | Required text constraints | goal/title/description constraints enforced programmatically | compiler tests |
| P0-16 | Determinism | repeated identical requests normalize to same result hash | 50-run test |
| P0-17 | Cache validation | invalid responses never cached | cache write test |
| P0-18 | Cache invalidation | schema/catalog/model version mismatch cannot serve stale plan | invalidation test |
| P0-19 | Secret hygiene | no committed credentials | secret scan |
| P0-20 | Tagged commit completeness | README/PPT/demo/docs referenced by submission exist in judged commit | release audit |

## B. P0 performance gates

Targets come from the supplied Theme 2 guide.

- [ ] Held-out semantic paraphrase cache hit rate **>=80%**.
- [ ] False cache-hit rate reported and acceptably low; do not inflate hit rate by lowering threshold recklessly.
- [ ] Cache-hit latency P95 **<=300 ms** on documented test machine.
- [ ] Cold-path latency P95 **<=8 s** on documented model/runtime environment.
- [ ] Model/index warmed before latency measurement.
- [ ] p50/p90/p95/p99 reported, not only average.
- [ ] Number of benchmark cases reported.

## C. Contract detail checks

### Goal

- [ ] exact required phrase pattern used;
- [ ] topic is coherent with actions;
- [ ] no unsupported extra prose.

### Title

- [ ] 2-3 words;
- [ ] sentence case;
- [ ] identifies core issue.

### Score

- [ ] float;
- [ ] 0.0 <= score <= 1.0;
- [ ] stable score logic documented.

### Action name

- [ ] Title Case;
- [ ] one screen or one feature;
- [ ] no two unrelated screens bundled.

### Description

- [ ] exactly 5-7 words;
- [ ] begins with `It will`;
- [ ] describes user benefit.

### Steps

- [ ] imperative;
- [ ] clear physical interaction;
- [ ] no web URL;
- [ ] no unsupported knowledge;
- [ ] no hidden multi-screen jumps inside a single action.

### Category

- [ ] `auto` only for actionable standard configuration screens;
- [ ] `critical` for disruptive/irreversible operations;
- [ ] `manual` for physical/service intervention;
- [ ] manual actions have no actionable deeplink.

### Deeplink

- [ ] copied verbatim from catalog;
- [ ] resolves to exact target, not merely a parent menu;
- [ ] semantic selection used metadata, not URI token text.

### Query variations

- [ ] 8-10 variations;
- [ ] genuinely diverse register/style;
- [ ] symptom meaning preserved;
- [ ] no new unsupported symptom inserted.

## D. P1 quality gates

- [ ] Hybrid screen retrieval beats or matches dense-only and BM25-only on held-out data.
- [ ] Parent-menu error rate explicitly measured.
- [ ] Low-confidence matcher rejects uncertain cases.
- [ ] Cache similarity threshold tuned on held-out positives and hard negatives.
- [ ] Multi-symptom complaints preserve both branches.
- [ ] Duplicate screen actions merge safely.
- [ ] Conflicting evidence is handled deterministically.
- [ ] Very long SIIS text does not overflow model/context unexpectedly.
- [ ] Empty/whitespace query returns a clean validation error.
- [ ] Unicode and typo-heavy queries do not crash normalization.
- [ ] Timeouts return machine-readable safe fallbacks.
- [ ] Dependency versions pinned or constrained reproducibly.

## E. P1 software engineering gates

- [ ] route handlers contain no core planning logic;
- [ ] provider interfaces have fake implementations for tests;
- [ ] no global mutable request state;
- [ ] index record IDs are stable;
- [ ] cache writes are transactional;
- [ ] logs are structured;
- [ ] exceptions do not leak secrets;
- [ ] Docker image starts on a clean machine;
- [ ] README setup commands tested literally;
- [ ] `ruff check .` passes;
- [ ] `mypy` passes at least core modules;
- [ ] `pytest` passes;
- [ ] coverage for core validators/retrieval/cache is high enough to be meaningful.

## F. P2 differentiation checks

- [ ] Action Graph provenance can be displayed in demo/debug mode.
- [ ] Semantic Case Lattice is measured against raw sentence-vector cache.
- [ ] Risk sequencer has versioned policy.
- [ ] Ablation report exists.
- [ ] Before/after or baseline comparison exists.
- [ ] Limitations are stated clearly.
- [ ] Innovation claims are linked to working code and metrics.

## G. Static audit commands

Adapt paths to the repo.

```bash
ruff check .
python -m mypy src/fixgraph
pytest -q
pytest -q tests/adversarial
python scripts/benchmark_cache.py
python scripts/benchmark_retrieval.py
python scripts/benchmark_latency.py
```

Search for suspicious hard-coded URLs/URIs:

```bash
grep -RInE 'https?://|www\.' src tests || true
grep -RIn 'bixby://' src tests || true
```

The second grep should show only fixtures/tests or code that reads exact values from catalog data. It should not reveal code constructing URI strings.

## H. Final technical sign-off

Release only if:

```text
P0 CONTRACT: PASS
P0 PERFORMANCE: PASS
TESTS: PASS
REPRODUCIBLE SETUP: PASS
SECRET SCAN: PASS
SUBMISSION COMMIT AUDIT: PASS
```

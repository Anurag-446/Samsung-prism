# Complete Sequential Coding Prompts

Use these prompts one at a time with a coding agent. Do not paste all prompts into a single run. Each prompt assumes the previous one has been completed and committed. Before accepting an agent's work, run the acceptance checks written under that prompt.

## Global context to prepend when the coding agent loses context

```text
We are building FixGraph for Samsung PRISM GenAI Hackathon 3.0, Theme 2: Smart Guided Troubleshooting Engine.
Hard constraints: strict supplied schema, POST /v1/troubleshoot, GET /health, pure JSON, zero web URL leakage, no hallucinated troubleshooting steps, exact deeplinks copied from provided deeplinks.json, semantic matching on descriptive metadata rather than masked URI strings, one action = one physical screen/feature, critical/destructive operations last, deterministic repeated outputs, semantic paraphrase cache target >=80%, cache-hit P95 <=300ms, cold-path P95 <=8s. Never weaken these constraints merely to make tests pass.
Architecture: untrusted LLM/parser -> evidence-grounded intermediate plan -> hybrid screen resolver -> exact catalog deeplink -> risk sequencer -> deterministic validation compiler -> cache only validated responses.
```

---

## Prompt 00 — Repository reconnaissance

```text
Act as a senior Python platform engineer. Inspect the entire repository before modifying anything. Identify all supplied starter assets including schema.py, queries.json, siis_responses.json, deeplinks.json, samples/, tests, docs and existing app code. Produce docs/REPO_AUDIT.md containing: file tree, each asset's schema, missing dependencies, conflicts with the challenge specification, existing tests, and a safe migration plan. Do not delete or rename challenge-provided files. Do not implement features yet. If an expected asset is absent, record it as absent rather than fabricating it.
```

Acceptance:
- complete file inventory;
- challenge-provided artifacts clearly distinguished from our files;
- no source changes except audit/documentation.

## Prompt 01 — Bootstrap project skeleton

```text
Create a production-shaped Python 3.11+ project named fixgraph while preserving supplied challenge assets. Add pyproject.toml, src/fixgraph package, tests directories, scripts directory, docs directory, .env.example, .gitignore and Dockerfile skeleton. Use FastAPI, Pydantic v2, pytest, ruff and mypy. Keep optional ML dependencies in a clearly named extra if practical. Add a Makefile or cross-platform task commands documented in README. Do not implement business logic yet. Ensure `python -m pytest` can run an empty/smoke suite.
```

## Prompt 02 — Freeze supplied data contracts

```text
Read the supplied schema.py in full. Reproduce its exact public data contract in src/fixgraph/contracts without silently changing enum names, defaults, optionality or field types. If import-through is safer, wrap rather than duplicate. Add contract tests that load the five supplied sample pairs and prove parse/serialize compatibility. Document any ambiguity in docs/CONTRACT_NOTES.md. Never alter schema.py merely to make our implementation easier.
```

## Prompt 03 — Configuration system

```text
Implement typed application settings with environment variables for model provider, model name, embedding model, similarity thresholds, cache DB path, data paths, timeouts and log level. No secret may be committed. Add startup validation and friendly error messages for missing required assets. Include .env.example with placeholders only.
```

## Prompt 04 — Challenge asset loaders

```text
Implement robust loaders for queries.json, siis_responses.json, deeplinks.json and any supplied sample directory. Use Pydantic/dataclasses for internal parsing. Validate malformed records early and fail startup with exact record identifiers. Compute SHA-256 fingerprints for schema/reference/deeplink assets. Add unit tests for good and intentionally corrupted fixtures.
```

## Prompt 05 — Deeplink catalog model

```text
Build an immutable DeeplinkCatalog abstraction. Preserve the exact deeplink URI string from each record. Build a retrieval document only from descriptive metadata such as description, message, qna_description, classes, control type and originalType. Explicitly exclude the masked URI text from semantic search text. Expose `get_by_id`, `iter_records`, `fingerprint` and `resolve_exact_uri(record_id)` APIs. Add a regression test proving no code constructs or mutates a bixby URI.
```

## Prompt 06 — URL hygiene gate

```text
Implement a URLLeakValidator that detects http://, https://, www., markdown links, HTML hrefs and common obfuscations in every user-visible text field of the final plan. It must not reject an allowed catalog-sourced `bixby://` value in the designated deeplink field. Add property-based tests and adversarial examples. The validator must operate after generation and before serialization.
```

## Prompt 07 — Query normalizer

```text
Implement deterministic query normalization: Unicode normalization, whitespace cleanup, casing normalization for matching, typo-tolerant tokenization, device/domain alias mapping, and preservation of the original query for output/audit. Do not remove semantically meaningful negation, chronology or trigger phrases such as 'after update'. Add unit tests over slang, punctuation, typos and mixed casing.
```

## Prompt 08 — Symptom atom extractor

```text
Implement a SymptomAtomExtractor interface with a deterministic baseline plus an LLM-backed implementation behind a provider interface. Output only a constrained intermediate schema containing device, domains, symptoms, trigger/context, entities and uncertainty. The LLM is not allowed to emit final steps or deeplinks here. Add a fake provider for tests and deterministic snapshot tests.
```

## Prompt 09 — Semantic case signature

```text
Build a canonical case-signature generator from normalized device/domain/symptom/trigger/constraints. Sort multi-valued fields stably so semantically identical cases produce the same signature regardless of input order. Persist a signature version. Add tests showing ten substantially different paraphrases of one issue collapse to the same or compatible signature while nearby but materially different issues do not.
```

## Prompt 10 — Embedding service

```text
Create an Embedder protocol and a local sentence-transformers implementation using a small CPU-friendly model. Batch-encode where possible. Add model warm-up and deterministic settings. Add a fake embedder for tests. Expose embedding dimension and model fingerprint so cache/index entries can be invalidated on model change.
```

## Prompt 11 — BM25 deeplink index

```text
Implement a BM25 index over descriptive deeplink metadata. Store stable record IDs. Add tokenization suited to Settings phrases. Provide top_k search with scores. Add tests for exact target screens and a test showing parent-menu-only matches are not automatically accepted.
```

## Prompt 12 — Dense deeplink index

```text
Implement a dense vector index over the same descriptive catalog records. Use FAISS if available, with a NumPy cosine fallback to keep the project portable. Persist or precompute embeddings on startup. Add tests for save/load consistency and stable record alignment.
```

## Prompt 13 — Hybrid screen resolver

```text
Create a ScreenResolver that combines BM25 and dense retrieval. Normalize scores, fuse top candidates, then apply deterministic metadata/intent consistency rules. Return a ranked candidate list with component scores and an overall confidence. Do not return a deeplink URI until a catalog record is selected. Reject low-confidence or conflicting matches rather than guessing. Add tests for screen-vs-parent-menu discrimination.
```

## Prompt 14 — Evidence segmentation and provenance

```text
Implement an EvidenceResolver. If request.siis_response is present, segment it into evidence units while retaining source IDs and offsets. If the project has provided indexed reference responses, support lookup against those assets. If no evidence exists, return an explicit no-context result; never silently substitute web knowledge. Add provenance IDs that can be attached to intermediate candidate actions.
```

## Prompt 15 — Evidence-grounded action extractor

```text
Implement an ActionExtractor that receives only the normalized complaint and resolved evidence units. It may use the configured LLM in structured-output mode to produce candidate actions, atomic imperative steps, evidence IDs and risk hints. It must not emit trusted deeplink URIs. Add a post-check requiring every candidate action to cite at least one evidence ID. Reject unsupported actions.
```

## Prompt 16 — One-action-one-screen grouper

```text
Implement grouping logic enforcing exactly one physical screen or feature per Action. Multiple interactions on the same screen may be grouped. If candidate steps cross screens, split the action. If two candidate actions resolve to the same screen and are semantically compatible, merge them deterministically. Add focused tests around over-granular and under-granular cases.
```

## Prompt 17 — Risk classifier

```text
Implement a deterministic disruption/risk classifier for actions. Use action category, keywords and metadata to assign tiers from inspection/reversible configuration through reboot/reset/manual repair. Keep the policy in a versioned configuration file. Add tests for factory reset, firmware update, safe mode, reboot, toggle, inspection and manual service cases.
```

## Prompt 18 — Action sequencer

```text
Implement stable risk-aware sequencing. Respect explicit evidence dependencies first, then sort by disruption tier. Critical/destructive actions must be last unless a hard dependency proves otherwise; in that case document the exception. Preserve deterministic output order. Add tests over mixed action sets.
```

## Prompt 19 — Final plan compiler

```text
Build a PlanCompiler that converts resolved internal actions into the exact challenge Goal/Action/StepGroup structures. Apply exact goal syntax, title casing/word-count rules, description word-count and prefix rules, score clamping, category mapping, and catalog deeplinks. Do not call an LLM for formatting. Add snapshot tests for supplied sample cases.
```

## Prompt 20 — Validation compiler

```text
Implement a validator pipeline returning structured errors and warnings. Include schema conformance, goal syntax, title length, description requirements, imperative-step checks, one-screen-per-action, URL leak, evidence grounding, catalog deeplink integrity, manual-action deeplink prohibition, action order, duplicate actions, score range and JSON-only serialization. Validation must run before any response can be cached.
```

## Prompt 21 — Deterministic repair pass

```text
Implement only safe deterministic repairs: whitespace/casing, legal truncation, score clamping, step dedupe, action reorder, URI replacement from selected catalog record and removal of forbidden URL fragments. Do not fabricate missing troubleshooting meaning. If the plan still fails after one repair pass, produce a safe fallback rather than looping.
```

## Prompt 22 — Safe fallback behavior

```text
Implement explicit fallback results for no_siis_context, no_match, invalid_plan, provider_timeout and low_confidence_screen. Fallback must conform to the public response contract and must not contain invented steps or deeplinks. Add tests for each failure path.
```

## Prompt 23 — Persistent semantic cache

```text
Implement a SQLite-backed CaseCache. Store only fully validated response JSON plus signature, canonical query, embedding, source/catalog/schema fingerprints, validation hash, created_at and hit_count. Use transactions and safe concurrent access. Never cache failed or partially repaired invalid plans.
```

## Prompt 24 — Two-stage cache matcher

```text
Implement exact canonical-signature lookup followed by semantic nearest-neighbor lookup. Add compatibility gates for domain, major symptom and trigger. Make threshold configurable. Return cache similarity and match reason in internal metadata. Ensure a battery-drain case cannot accidentally serve a battery-not-charging plan merely because vocabulary overlaps.
```

## Prompt 25 — Cache invalidation

```text
Invalidate or bypass cache entries if schema version, catalog fingerprint, evidence/reference fingerprint, embedding model fingerprint or case-signature version is incompatible. Add migration-safe behavior and tests proving stale entries are not served.
```

## Prompt 26 — Query variation generator

```text
Implement query_variations generation producing 8-10 materially distinct paraphrases with formal, casual, keyword-only, typo-inclusive and frustrated styles. This field is for the required output/evaluation behavior; it must not introduce unsupported symptoms. Deduplicate variations semantically and lexically. Add tests that each variation preserves the same symptom set.
```

## Prompt 27 — FastAPI endpoints

```text
Implement POST /v1/troubleshoot and GET /health. Route handlers should orchestrate service calls only. Request includes query and optional siis_response. Return pure JSON. Include operational meta fields only if permitted by the provided API wrapper/spec; do not mutate the supplied Goal schema. Add OpenAPI docs for development but ensure the judged endpoint matches the exact required path.
```

## Prompt 28 — Health readiness

```text
Make /health return 200 with {"status":"ok"} only when schema, catalog, indexes and cache are initialized and the configured model/provider passes readiness requirements. Otherwise return non-200 with a concise machine-readable reason. Add startup tests.
```

## Prompt 29 — Observability

```text
Add structured logs and an internal RunMetrics object capturing total latency, cache hit, cache similarity, retrieval latency, LLM latency, validation repairs, deeplink confidence, token counts and estimated cost where available. Do not place logs in the API response unless the supplied contract allows metadata outside the Goal payload. Redact secrets.
```

## Prompt 30 — Determinism hardening

```text
Audit every source of nondeterminism: model temperature, unordered sets/dicts, vector tie-breaking, async task completion order, floating thresholds and timestamp-dependent behavior. Use temperature 0 or equivalent structured deterministic settings, stable sorts and deterministic tie breakers. Add a test that runs the same request 50 times and compares normalized response hashes.
```

## Prompt 31 — Reference sample regression suite

```text
Turn every supplied sample pair into a regression test. Validate schema, exact deeplink provenance, action granularity, action order, word constraints and zero URL leakage. Do not overfit by hardcoding sample-query strings; assert behavior through the normal pipeline.
```

## Prompt 32 — Adversarial hygiene suite

```text
Create tests/adversarial with at least 100 generated/manual cases: explicit web URL in SIIS text, prompt injection asking for a support website, malformed markdown link, fake bixby URI, unsupported hardware repair, mixed symptoms, contradictory symptoms, typo-heavy text, very long input, empty input, duplicate actions, parent-menu trap, destructive-first wording and irrelevant SIIS. The system must remain contract-safe.
```

## Prompt 33 — Paraphrase cache benchmark

```text
Build scripts/benchmark_cache.py. For each canonical issue, hold out paraphrases that were not used to warm the cache. Measure hit rate, false-hit rate, confusion pairs and latency. Report >=80% target separately from false-positive rate. Save machine-readable JSON and a Markdown summary under reports/.
```

## Prompt 34 — Screen-resolution benchmark

```text
Create an evaluation set of action-to-target-screen mappings from supplied samples plus manually verified cases. Compare BM25-only, dense-only, hybrid and hybrid+consistency rerank. Report top-1 accuracy, top-3 recall, parent-menu error rate and low-confidence rejection rate. Never fabricate ground truth; clearly mark manually labeled cases.
```

## Prompt 35 — Latency benchmark

```text
Build a repeatable benchmark for at least warm cache hits and cold-path generation. Measure p50, p90, p95 and p99. Warm the process before measurement. Record machine specifications. Report cache-hit target <=300 ms P95 and cold-path target <=8 s P95. Separate model/provider network time from local pipeline time.
```

## Prompt 36 — Load/stress test

```text
Create a lightweight concurrent load test with a configurable mix of cache hits and cold misses. Measure throughput, error rate, DB contention and latency percentiles. Ensure SQLite access does not serialize the whole service unnecessarily. The goal is robustness evidence, not unrealistic scale claims.
```

## Prompt 37 — Ablation study

```text
Implement reproducible ablations: dense-only vs BM25-only vs hybrid vs hybrid+rerank; raw-query cache vs signature+semantic cache; LLM formatting vs deterministic compiler if an old baseline exists. Produce reports/ablation.md with metrics and interpretations. Do not claim statistical significance without enough data.
```

## Prompt 38 — Docker and clean-room setup

```text
Finish Dockerfile and optionally docker-compose if genuinely needed. A fresh clone must build and run with documented commands. No local absolute paths. Mount/provide challenge assets through documented locations. Add a smoke test that builds the image, starts the API, waits for /health and sends one request.
```

## Prompt 39 — README

```text
Write a judge-friendly README: problem, FixGraph concept, architecture diagram, novelty, exact setup, data placement, run commands, API examples, test commands, benchmark commands, results table, limitations, ethical/AI disclosure note, demo link placeholder and release-tag instructions. Do not exaggerate benchmark results; pull them from generated reports.
```

## Prompt 40 — Security and secret scan

```text
Audit for API keys, tokens, credentials, personal data, absolute local paths, copyrighted/proprietary data accidentally committed and verbose logs. Add a secret-scan command if practical. Ensure .env is ignored and only .env.example is committed.
```

## Prompt 41 — Submission PPT evidence extractor

```text
Create docs/PPT_EVIDENCE.md mapping each provided Samsung submission slide to exact evidence in the repo: screenshots to capture, metrics to cite, architecture figure, limitations, and differentiators. Do not modify the official PPT template in this task. Flag any slide for which evidence is not yet available.
```

## Prompt 42 — Five-minute demo harness

```text
Create scripts/demo.py or a minimal demo UI that can execute three prepared scenarios: cold multi-symptom case, unseen paraphrase cache hit, and adversarial URL/unsupported-action safety case. Print only data derived from real API calls. Add a --reset-demo-cache option and a --warm-case option so the demo is reproducible.
```

## Prompt 43 — AI disclosure ledger

```text
Create docs/AI_USAGE_LEDGER.md with a table for feature name, origin (self/AI/both), AI tool, prompt ID, output summary, human modifications, and files affected. Populate only entries supported by git history/current work. This should make the supplied AI disclosure form easy to complete honestly.
```

## Prompt 44 — Full technical red-team

```text
Act as a hostile evaluator. Try to break every non-negotiable challenge rule. Run the complete test suite and inspect code paths manually. Create reports/RED_TEAM.md with each attempted failure, reproduction command, observed result, severity and fix status. Do not fix by deleting tests or loosening assertions.
```

## Prompt 45 — Performance red-team

```text
Profile startup, fast path and cold path. Find unnecessary model calls, repeated embeddings, excessive JSON copying, synchronous blocking in async handlers, unbounded context and DB hot spots. Optimize only after measuring. Re-run benchmarks and show before/after numbers.
```

## Prompt 46 — Final contract audit

```text
Re-open the original challenge PDF and supplied schema.py. Compare every current field, endpoint, rule and performance target against the implementation. Produce reports/FINAL_CONTRACT_AUDIT.md with PASS/FAIL/NOT-VERIFIABLE for each requirement and exact file/test evidence. Any FAIL blocks release.
```

## Prompt 47 — Reproducibility audit

```text
Pretend you are a judge using a new laptop. Follow only README instructions from a clean environment. Record every missing step, implicit dependency, unavailable asset assumption or platform-specific command. Fix documentation/build scripts until clean-room setup works.
```

## Prompt 48 — Release preparation

```text
Prepare the repository for final judging without tagging yet. Ensure all referenced PPT/demo/docs files exist in the final commit, generated reports are current, tests are green, no secrets exist, and README links are valid. Create reports/RELEASE_CANDIDATE.md with commit hash placeholder, test summary, benchmark summary and remaining blockers.
```

## Prompt 49 — Final go/no-go

```text
Run the final acceptance checklist from docs/16_FINAL_ACCEPTANCE_CHECKLIST.md. Return GO only if every P0 item passes. If any P0 item fails, return NO-GO with exact commands/files required to fix it. Do not create the final release tag automatically.
```

## Prompt 50 — Post-approval tag command

Run this manually only after the team verifies the exact commit intended for judging:

```bash
git status
git log -1 --oneline
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "Samsung PRISM GenAI Hackathon 2026 final submission"
git push origin PRISM_GENAI_HACKATHON_Y2026
```

Then verify the tag on the remote repository and confirm that PPT/demo/documentation references correspond to that tagged commit.

# Test and Evaluation Plan

## 1. Testing pyramid

### Unit tests

Focus on:

- normalization;
- signature generation;
- validators;
- action ordering;
- catalog exact-match integrity;
- cache invalidation;
- score fusion;
- safe repair.

### Integration tests

Focus on:

- asset load -> query -> plan -> validation;
- cache miss -> write -> paraphrase hit;
- provider timeout -> safe fallback;
- low-confidence screen -> safe fallback;
- catalog change -> old cache rejected.

### End-to-end tests

Call the actual FastAPI endpoint and parse response with the supplied schema.

## 2. Required evaluation sets

### A. Supplied sample set

Use every challenge-provided sample pair as regression material.

### B. Paraphrase holdout set

For each canonical issue:

- 3 formal paraphrases;
- 3 conversational paraphrases;
- 2 keyword-style queries;
- 2 typo/noisy queries;
- 2 frustrated/emotional queries.

Warm cache using only a subset. Evaluate on unseen variants.

### C. Hard negative set

Examples:

- battery fast drain vs battery not charging;
- screen flicker vs screen brightness too low;
- app slow vs phone overheating;
- camera focus vs camera permissions.

Purpose: prevent unsafe semantic-cache overmatching.

### D. Parent-menu traps

Create cases where a generic parent screen has high lexical similarity but a child/target screen is the correct destination.

### E. Adversarial hygiene set

At least 100 cases across:

- web URLs;
- markdown links;
- HTML links;
- prompt injection;
- fake deeplink requests;
- unsupported repairs;
- empty evidence;
- contradictory evidence;
- duplicate steps;
- destructive-first instructions;
- long inputs;
- Unicode/typos;
- multiple symptoms.

## 3. Metrics

### Schema validity

```text
valid_outputs / total_outputs
```

Target: 100% on submitted evaluation suite.

### URL leakage rate

```text
responses_with_forbidden_url / total_responses
```

Target: 0%.

### Fabricated deeplink rate

```text
emitted_deeplinks_not_exactly_in_catalog / all_emitted_deeplinks
```

Target: 0%.

### Screen top-1 accuracy

```text
correct_target_screen_at_rank1 / labeled_actions
```

### Screen top-3 recall

```text
correct_screen_in_top3 / labeled_actions
```

### Parent-menu error rate

```text
wrong_parent_menu_selected / labeled_actions
```

### Paraphrase cache hit rate

```text
correct_cache_hits / eligible_heldout_paraphrases
```

Theme target: >=80%.

### False-hit rate

```text
incorrect_cache_reuse / all_cache_hits
```

Report this beside hit rate. A high hit rate with dangerous false reuse is not success.

### Latency

Report p50, p90, p95, p99.

Two populations:

- validated cache hits;
- cold path.

Targets:

- cache hit P95 <=300 ms;
- cold path P95 <=8 s.

### Determinism

```text
unique_normalized_response_hashes across N identical runs
```

Target: 1.

## 4. Ablations

### Screen retrieval

| Variant | Top-1 | Top-3 | Parent-menu errors | Mean local latency |
|---|---:|---:|---:|---:|
| BM25 only | | | | |
| Dense only | | | | |
| Hybrid | | | | |
| Hybrid + consistency | | | | |

### Cache

| Variant | Hit rate | False-hit rate | P95 |
|---|---:|---:|---:|
| Raw sentence embedding | | | |
| Canonical signature only | | | |
| Signature + semantic fallback | | | |

## 5. Benchmark methodology rules

- document machine CPU/RAM/OS;
- document model/provider;
- warm models before timed run;
- exclude setup/index build from request latency but report setup separately;
- run enough samples to make percentiles meaningful;
- save raw JSON/CSV results;
- commit benchmark scripts;
- do not manually edit reported metric files.

## 6. Test commands

Recommended:

```bash
pytest -q
pytest -q tests/unit
pytest -q tests/integration
pytest -q tests/e2e
pytest -q tests/adversarial
python scripts/benchmark_retrieval.py
python scripts/benchmark_cache.py
python scripts/benchmark_latency.py
python scripts/run_ablation.py
```

## 7. Hidden-test mindset

Assume hidden tests will target:

- exact wording/word-count edge cases;
- unusual paraphrases;
- low-confidence screen matches;
- parent-menu confusion;
- URL injection;
- URI fabrication;
- destructive action ordering;
- missing context;
- repeated inputs/determinism;
- latency on warmed cached cases.

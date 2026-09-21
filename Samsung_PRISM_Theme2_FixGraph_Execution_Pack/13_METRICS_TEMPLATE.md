# System Performance and Evaluation Report

> Fill this file using generated benchmark outputs. Do not hand-invent numbers.

## 1. Environment

| Item | Value |
|---|---|
| Commit | |
| Release tag | |
| Date | |
| OS | |
| CPU | |
| RAM | |
| Python | |
| LLM provider/model | |
| Embedding model | |
| Catalog fingerprint | |
| Reference fingerprint | |

## 2. Contract compliance

| Metric | Value | Target | Pass? |
|---|---:|---:|---|
| Schema-valid responses | | 100% | |
| Web URL leakage | | 0% | |
| Fabricated deeplinks | | 0% | |
| Unsupported actions reaching final output | | 0% | |
| Manual actions with actionable deeplink | | 0 | |
| Deterministic response hashes for repeated case | | 1 unique | |

## 3. Screen resolution

| Variant | Top-1 accuracy | Top-3 recall | Parent-menu error | Rejection rate |
|---|---:|---:|---:|---:|
| BM25 | | | | |
| Dense | | | | |
| Hybrid | | | | |
| Hybrid + consistency | | | | |

## 4. Semantic cache

| Metric | Value | Target |
|---|---:|---:|
| Held-out paraphrase hit rate | | >=80% |
| False-hit rate | | report |
| Exact-signature hit share | | report |
| Semantic-fallback hit share | | report |

Hard-negative confusions observed:

1. 
2. 
3. 

## 5. Latency

### Cache hit

| p50 | p90 | p95 | p99 | n |
|---:|---:|---:|---:|---:|
| | | | | |

Target: P95 <=300 ms.

### Cold path

| p50 | p90 | p95 | p99 | n |
|---:|---:|---:|---:|---:|
| | | | | |

Target: P95 <=8 s.

## 6. Resource/cost

| Metric | Value |
|---|---:|
| Mean input tokens/cold request | |
| Mean output tokens/cold request | |
| Mean estimated provider cost/cold request | |
| Cache-hit provider cost | expected 0 |
| Process RSS after warm-up | |
| Index build time | |

## 7. Ablation interpretation

### Hybrid retrieval

What improved?  
What regressed?  
Why keep/remove it?

### Semantic Case Lattice

What improved over raw sentence vector cache?  
What failure cases remain?

## 8. Adversarial evaluation

| Category | Cases | Failures | Notes |
|---|---:|---:|---|
| URL injection | | | |
| fake deeplinks | | | |
| unsupported knowledge | | | |
| parent-menu traps | | | |
| destructive-first | | | |
| typo/noisy language | | | |
| multi-symptom | | | |
| missing context | | | |

## 9. Limitations

List only real observed limits. Examples:

- coverage limited by supplied SIIS/reference assets;
- catalog may not contain every valid Settings screen;
- model/provider latency affects cold path;
- semantic-cache threshold trades hit rate against false positives;
- device/OS-version specificity may be incomplete if not encoded in starter data.

## 10. Final result summary

```text
Contract safety: PASS/FAIL
Screen resolution: <measured summary>
Cache hit rate: <value>
Cache false-hit rate: <value>
Fast-path P95: <value>
Cold-path P95: <value>
Ready for release: YES/NO
```

"""Combined prewarm + held-out paraphrase benchmark pipeline.
Run after setting FIXGRAPH_LLM_PROVIDER=mock.
"""
import json
import os
import sqlite3
import time

# Step 1: Prewarm
from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService

DB_PATH = "data/cache.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"[prewarm] Deleted old cache: {DB_PATH}")

assets = build_challenge_assets(settings, "development")
catalog = build_catalog(settings, assets, "development")
service = TroubleshootService(catalog=catalog, cache_db_path=DB_PATH)

from fixgraph.data.manager_cases import load_manager_cases  # noqa: E402

cases = load_manager_cases(
    "manager_assets/Theme 2/input.txt",
    "manager_assets/Theme 2/siis_responses.json",
)

print(f"\n[prewarm] Warming {len(cases)} manager cases with SIIS evidence...")
prewarm_start = time.time()
successes, failures = 0, 0
for case in cases:
    req = TroubleshootRequest(query=case.query, siis_response=case.siis.content)
    outcome = service.troubleshoot(req)
    if outcome.status == "success" and outcome.goal is not None:
        successes += 1
        status_str = f"OK (source={outcome.source}, actions={len(outcome.goal.actions)})"
    else:
        failures += 1
        status_str = f"FAIL (source={outcome.source}, reason={outcome.failure_reason})"
    print(f"  [{successes+failures:2d}/20] {case.query[:60]:60s} -> {status_str}")

prewarm_elapsed = time.time() - prewarm_start

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cache_entries")
    cache_count = cur.fetchone()[0]
    conn.close()
except Exception:
    cache_count = "unknown"

print(f"\n[prewarm] Done in {prewarm_elapsed:.1f}s")
print(f"[prewarm] Cache entries: {cache_count}")
print(f"[prewarm] Successes: {successes} / Failures: {failures}")

# Step 2: Benchmark with held-out paraphrases
print("\n[benchmark] Running held-out paraphrase benchmark...")

with open("eval/cache/manager_paraphrases.json", "r", encoding="utf-8") as f:
    paraphrases = json.load(f)

with open("eval/cache/manager_hard_negatives.json", "r", encoding="utf-8") as f:
    hard_negatives = json.load(f)

tp, fn, tn, fp = 0, 0, 0, 0
total_latency = 0.0
per_query_results = []

all_queries = paraphrases + hard_negatives
for item in all_queries:
    q = item["query"]
    expected_hit = item.get("expected_hit", True)

    req = TroubleshootRequest(query=q, siis_response=None)
    t0 = time.time()
    outcome = service.troubleshoot(req)
    latency = (time.time() - t0) * 1000
    total_latency += latency

    is_hit = outcome.source == "semantic_cache"

    if expected_hit and is_hit:
        tp += 1; result = "TP"
    elif expected_hit and not is_hit:
        fn += 1; result = "FN"
        print(f"  [MISS ] {q[:80]}")
    elif not expected_hit and not is_hit:
        tn += 1; result = "TN"
    else:
        fp += 1; result = "FP"
        print(f"  [FALSE] {q[:80]}")

    per_query_results.append({
        "query": q, "expected_hit": expected_hit,
        "actual_hit": is_hit, "source": outcome.source,
        "latency_ms": round(latency, 2), "result": result,
    })

total = tp + fn + tn + fp
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
avg_lat = total_latency / total if total > 0 else 0

summary = f"""
=== BGE CACHE BENCHMARK RESULTS ===
Prewarm: {successes}/20 canonical cases succeeded in {prewarm_elapsed:.1f}s
Cache DB entries: {cache_count}

Test set: {len(paraphrases)} paraphrase positives + {len(hard_negatives)} hard negatives

True Positives  (Paraphrase Cache Hits):   {tp:3d}
False Negatives (Missed Paraphrase Hits):  {fn:3d}
True Negatives  (Correct Hard Neg Misses): {tn:3d}
False Positives (Incorrect Hits on Neg):   {fp:3d}

Hit Rate (Recall):   {recall*100:6.2f}%
Precision:           {precision*100:6.2f}%
F1 Score:            {f1*100:6.2f}%
False Positive Rate: {fpr*100:6.2f}%
Avg Latency:         {avg_lat:.2f}ms
==================================
"""
print(summary)

# Write evidence
os.makedirs("release_evidence", exist_ok=True)

evidence_md = f"""# BGE Semantic Cache Benchmark — Held-Out Paraphrase Evaluation

## Prewarm Evidence
- **Cases prewarmed**: {successes}/20 canonical manager queries with real SIIS evidence
- **Cache entries written**: {cache_count}
- **Prewarm latency**: {prewarm_elapsed:.1f}s

## Benchmark Design
- **Test set**: {len(paraphrases)} held-out paraphrase variants (not used during prewarm)
- **Hard negatives**: {len(hard_negatives)} adversarial cross-domain queries
- **Cache invariant**: CACHE HIT = ZERO LLM CALLS

## Results
```
{summary}```

## Per-Query Detail (Misses & False Positives)
"""
for r in per_query_results:
    if r["result"] in ("FN", "FP"):
        evidence_md += f"\n- [{r['result']}] `{r['query'][:100]}` (source={r['source']}, latency={r['latency_ms']:.0f}ms)"

with open("release_evidence/BGE_CACHE_EVALUATION.md", "w", encoding="utf-8") as f:
    f.write(evidence_md)

with open("release_evidence/cache_benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "prewarm": {
            "successes": successes, "failures": failures,
            "cache_entries": cache_count,
            "elapsed_s": round(prewarm_elapsed, 2),
        },
        "benchmark": {
            "total": total, "tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "recall_pct": round(recall * 100, 2),
            "precision_pct": round(precision * 100, 2),
            "f1_pct": round(f1 * 100, 2),
            "fpr_pct": round(fpr * 100, 2),
            "avg_latency_ms": round(avg_lat, 2),
        },
        "per_query": per_query_results,
    }, f, indent=2)

print("[benchmark] Evidence written to release_evidence/")

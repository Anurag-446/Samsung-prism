"""
BGE Semantic Cache Benchmark — held-out paraphrase evaluation.

Uses eval/cache/manager_paraphrases.json (true held-out paraphrases, different from
canonical prewarm queries) and eval/cache/manager_hard_negatives.json as the test set.

This benchmark is the ONLY valid measurement of cache recall:
- Positives: paraphrased user queries that SHOULD hit the cache (expected_hit=True)
- Negatives: hard negatives that MUST NOT hit the cache (expected_hit=False)
"""
import json
import time

from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService


def main():
    assets = build_challenge_assets(settings, "development")
    catalog = build_catalog(settings, assets, "development")
    service = TroubleshootService(catalog=catalog)

    # Load held-out paraphrase benchmark (expected_hit label from dataset)
    with open("eval/cache/manager_paraphrases.json", "r", encoding="utf-8") as f:
        paraphrases = json.load(f)

    # Load hard negatives
    with open("eval/cache/manager_hard_negatives.json", "r", encoding="utf-8") as f:
        hard_negatives = json.load(f)

    tp, fn, tn, fp = 0, 0, 0, 0
    total_latency = 0
    per_query_results = []

    all_queries = paraphrases + hard_negatives
    for item in all_queries:
        q = item["query"]
        expected_hit = item.get("expected_hit", True)

        req = TroubleshootRequest(query=q, siis_response=None)
        start_t = time.time()
        outcome = service.troubleshoot(req)
        latency = (time.time() - start_t) * 1000
        total_latency += latency

        is_hit = outcome.source == "semantic_cache"

        if expected_hit and is_hit:
            tp += 1
            result = "TP"
        elif expected_hit and not is_hit:
            fn += 1
            result = "FN"
            print(f"[BENCHMARK] Missed Hit: {q}")
        elif not expected_hit and not is_hit:
            tn += 1
            result = "TN"
        else:
            fp += 1
            result = "FP"
            print(f"[BENCHMARK] False Positive: {q}")

        per_query_results.append({
            "query": q,
            "expected_hit": expected_hit,
            "actual_hit": is_hit,
            "source": outcome.source,
            "latency_ms": round(latency, 2),
            "result": result,
        })

    total = tp + fp + tn + fn
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    avg_latency = total_latency / total if total > 0 else 0

    summary = f"""Total queries: {total}
  Paraphrase positives: {len(paraphrases)} | Hard negatives: {len(hard_negatives)}
True Positives (Paraphrase Cache Hits): {tp}
False Negatives (Missed Paraphrase Hits): {fn}
True Negatives (Correct Hard Neg Misses): {tn}
False Positives (Incorrect Hits on Hard Neg): {fp}
Hit Rate (Recall): {recall*100:.2f}%
Precision: {precision*100:.2f}%
F1 Score: {f1*100:.2f}%
False Positive Rate: {fpr*100:.2f}%
Avg Latency: {avg_latency:.2f}ms
"""

    import os
    os.makedirs("release_evidence", exist_ok=True)

    evidence_md = f"""# BGE Semantic Cache Benchmark — Held-Out Paraphrase Evaluation

## Benchmark Design
- **Test set**: {len(paraphrases)} held-out paraphrase variants (not used during prewarm)
- **Negatives**: {len(hard_negatives)} hard negatives (adversarial cross-domain queries)
- **Prewarm source**: manager_assets/Theme 2/input.txt (20 canonical queries)
- **Cache invariant**: CACHE HIT = ZERO LLM CALLS

## Results

```
{summary}```

## Per-Query Results (Misses & False Positives Only)
"""
    for r in per_query_results:
        if r["result"] in ("FN", "FP"):
            evidence_md += f"\n- [{r['result']}] `{r['query'][:100]}...` (source: {r['source']}, latency: {r['latency_ms']:.0f}ms)"

    with open("release_evidence/BGE_CACHE_EVALUATION.md", "w", encoding="utf-8") as f:
        f.write(evidence_md)

    with open("release_evidence/cache_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total,
                "tp": tp, "fn": fn, "tn": tn, "fp": fp,
                "recall_pct": round(recall * 100, 2),
                "precision_pct": round(precision * 100, 2),
                "f1_pct": round(f1 * 100, 2),
                "fpr_pct": round(fpr * 100, 2),
                "avg_latency_ms": round(avg_latency, 2),
            },
            "per_query": per_query_results,
        }, f, indent=2)

    print(summary)


if __name__ == "__main__":
    main()

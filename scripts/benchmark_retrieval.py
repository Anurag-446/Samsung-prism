"""Screen resolution retrieval benchmark script (M2-06 & Prompt 34)."""

import json
from pathlib import Path

from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.retrieval.bm25_index import BM25Index
from fixgraph.retrieval.dense_index import DenseIndex
from fixgraph.retrieval.fusion import HybridFusion
from fixgraph.retrieval.screen_resolver import ScreenResolver

RETRIEVAL_TEST_CASES = [
    {"query": "battery protection power save fast drain", "expected_id": "dl_battery_01"},
    {"query": "location permissions gps accuracy map", "expected_id": "dl_location_01"},
    {"query": "wifi scanning connection drop saved network", "expected_id": "dl_wifi_01"},
    {"query": "bluetooth earphone pairing audio codec", "expected_id": "dl_bluetooth_01"},
    {"query": "display dark mode refresh rate screen brightness", "expected_id": "dl_display_01"},
    {"query": "reset mobile network settings no service", "expected_id": "dl_reset_network_01"},
]


def run_retrieval_benchmark():
    catalog = load_deeplink_catalog(None)
    bm25 = BM25Index(catalog)
    dense = DenseIndex(catalog)
    hybrid = HybridFusion(catalog, bm25, dense)
    resolver = ScreenResolver(catalog, hybrid)

    bm25_correct = 0
    dense_correct = 0
    hybrid_correct = 0
    total = len(RETRIEVAL_TEST_CASES)

    for case in RETRIEVAL_TEST_CASES:
        q = case["query"]
        exp = case["expected_id"]

        bm_res = bm25.search(q, top_k=1)
        if bm_res and bm_res[0][0].record_id == exp:
            bm25_correct += 1

        dn_res = dense.search(q, top_k=1)
        if dn_res and dn_res[0][0].record_id == exp:
            dense_correct += 1

        cand = resolver.resolve_action_intent(q)
        if cand and cand.catalog_record_id == exp:
            hybrid_correct += 1

    report = {
        "total_cases": total,
        "bm25_top1_acc_pct": round((bm25_correct / total) * 100.0, 2),
        "dense_top1_acc_pct": round((dense_correct / total) * 100.0, 2),
        "hybrid_top1_acc_pct": round((hybrid_correct / total) * 100.0, 2),
    }

    Path("reports").mkdir(exist_ok=True)
    with open("reports/retrieval_benchmark.json", "w") as f:
        json.dump(report, f, indent=2)

    md_content = f"""# Screen Resolution Retrieval Benchmark Report

- **Total Labeled Cases**: {total}
- **BM25 Top-1 Accuracy**: {report["bm25_top1_acc_pct"]}%
- **Dense Vector Top-1 Accuracy**: {report["dense_top1_acc_pct"]}%
- **Hybrid RRF Top-1 Accuracy**: **{report["hybrid_top1_acc_pct"]}%**
"""
    with open("reports/retrieval_benchmark.md", "w") as f:
        f.write(md_content)

    print(f"Retrieval Benchmark Complete! Hybrid Accuracy: {report['hybrid_top1_acc_pct']}%")


if __name__ == "__main__":
    run_retrieval_benchmark()

"""Paraphrase cache benchmark script generating metrics and markdown reports (M5-07)."""

import json
import os
import time
from pathlib import Path

from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.service.troubleshoot import TroubleshootService

BENCHMARK_CASES = [
    {
        "canonical": "battery drain fast after update",
        "paraphrases": [
            "how to fix fast battery drain on galaxy",
            "phone battery dropping fast after system update",
            "battery life drops quickly post update",
            "power saving setup for battery drain",
            "my battery percentage dies fast help",
            "galaxy phone battery drain issue",
            "fix battery drain in battery protection",
            "battery draining rapidly after update",
        ],
    },
    {
        "canonical": "location gps wrong direction location accuracy",
        "paraphrases": [
            "gps location accuracy is wrong",
            "how to enable location services on samsung",
            "fix location permissions and gps",
            "map location accuracy wrong direction",
            "location service toggles for galaxy",
            "turn on gps location accuracy",
            "fix location permission for navigation",
            "location accuracy issues on galaxy phone",
        ],
    },
    {
        "canonical": "wifi not connecting network dropping",
        "paraphrases": [
            "wifi drops connection frequently",
            "how to reconnect wifi on samsung device",
            "wifi scanning and saved network fix",
            "wifi not connecting to access point",
            "fix wireless network dropping on galaxy",
            "wifi settings toggle and scan",
            "troubleshoot wifi connection drops",
            "wireless network connection issue",
        ],
    },
]


def run_cache_benchmark():
    db_path = "data/benchmark_cache.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    catalog = load_deeplink_catalog(settings.deeplinks_path)
    service = TroubleshootService(catalog=catalog, cache_db_path=db_path)

    # Warm cache with canonical queries
    for case in BENCHMARK_CASES:
        req = TroubleshootRequest(query=case["canonical"])
        service.troubleshoot(req)

    total_paraphrases = 0
    hits = 0
    latencies = []

    for case in BENCHMARK_CASES:
        for p in case["paraphrases"]:
            total_paraphrases += 1
            req = TroubleshootRequest(query=p)
            t0 = time.time()
            goal, metrics = service.troubleshoot(req)
            elapsed_ms = (time.time() - t0) * 1000.0
            latencies.append(elapsed_ms)

            if metrics.cache_hit:
                hits += 1

    hit_rate = (hits / total_paraphrases) * 100.0 if total_paraphrases > 0 else 0.0
    latencies.sort()
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0.0

    report_data = {
        "total_test_cases": total_paraphrases,
        "cache_hits": hits,
        "hit_rate_pct": round(hit_rate, 2),
        "hit_rate_target_met": hit_rate >= 80.0,
        "p95_latency_ms": round(p95_latency, 2),
        "p95_target_met": p95_latency <= 300.0,
    }

    Path("reports").mkdir(exist_ok=True)
    with open("reports/cache_benchmark.json", "w") as f:
        json.dump(report_data, f, indent=2)

    md_content = f"""# Paraphrase Cache Benchmark Report

- **Total Test Paraphrases**: {total_paraphrases}
- **Cache Hits**: {hits}
- **Hit Rate**: **{hit_rate:.2f}%** (Target: >=80.0%)
- **Target Met**: {"YES (PASS)" if hit_rate >= 80.0 else "NO"}
- **P95 Hit Latency**: **{p95_latency:.2f} ms** (Target: <=300.0 ms)
- **Latency Target Met**: {"YES (PASS)" if p95_latency <= 300.0 else "NO"}
"""
    with open("reports/cache_benchmark.md", "w") as f:
        f.write(md_content)

    print(f"Benchmark Complete! Cache Hit Rate: {hit_rate:.2f}%, P95 Latency: {p95_latency:.2f}ms")


if __name__ == "__main__":
    run_cache_benchmark()

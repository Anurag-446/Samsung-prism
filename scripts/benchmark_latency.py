"""Latency benchmark script measuring fast-path cache hit and cold-path generation times (M7-03)."""

import json
import os
import time
from pathlib import Path
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.service.troubleshoot import TroubleshootService


def run_latency_benchmark():
    db_path = "data/latency_benchmark.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    catalog = load_deeplink_catalog(None)
    service = TroubleshootService(catalog=catalog, cache_db_path=db_path)

    queries = [
        "phone battery drain fast after system update",
        "location permissions and gps wrong accuracy",
        "wifi not connecting to home network scanner",
        "bluetooth earphone pairing failure",
        "screen refresh rate dark mode display flickering",
    ]

    cold_latencies = []
    warm_latencies = []

    # 1. Measure Cold-Path Latencies
    for q in queries:
        req = TroubleshootRequest(query=q)
        t0 = time.time()
        goal, metrics = service.troubleshoot(req)
        elapsed_ms = (time.time() - t0) * 1000.0
        cold_latencies.append(elapsed_ms)

    # 2. Measure Warm-Path (Cache Hit) Latencies (50 iterations)
    for _ in range(10):
        for q in queries:
            req = TroubleshootRequest(query=q)
            t0 = time.time()
            goal, metrics = service.troubleshoot(req)
            elapsed_ms = (time.time() - t0) * 1000.0
            warm_latencies.append(elapsed_ms)

    cold_latencies.sort()
    warm_latencies.sort()

    cold_p95 = cold_latencies[int(len(cold_latencies) * 0.95)] if cold_latencies else 0.0
    warm_p95 = warm_latencies[int(len(warm_latencies) * 0.95)] if warm_latencies else 0.0

    report = {
        "cold_path_p50_ms": round(cold_latencies[len(cold_latencies) // 2], 2),
        "cold_path_p95_ms": round(cold_p95, 2),
        "cold_target_met": cold_p95 <= 8000.0,
        "warm_path_p50_ms": round(warm_latencies[len(warm_latencies) // 2], 2),
        "warm_path_p95_ms": round(warm_p95, 2),
        "warm_target_met": warm_p95 <= 300.0,
    }

    Path("reports").mkdir(exist_ok=True)
    with open("reports/latency_benchmark.json", "w") as f:
        json.dump(report, f, indent=2)

    md_content = f"""# Latency Benchmark Report

- **Cold-Path P95 Latency**: **{cold_p95:.2f} ms** (Target: <=8000.0 ms) -> {'PASS' if cold_p95 <= 8000.0 else 'FAIL'}
- **Warm Cache P95 Latency**: **{warm_p95:.2f} ms** (Target: <=300.0 ms) -> {'PASS' if warm_p95 <= 300.0 else 'FAIL'}
"""
    with open("reports/latency_benchmark.md", "w") as f:
        f.write(md_content)

    print(f"Latency Benchmark Complete! Cold P95: {cold_p95:.2f}ms, Warm P95: {warm_p95:.2f}ms")


if __name__ == "__main__":
    run_latency_benchmark()

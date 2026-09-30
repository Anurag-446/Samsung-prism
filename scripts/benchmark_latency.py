import statistics

from fixgraph.config import settings


def run_benchmark():
    from fixgraph.bootstrap import build_catalog, build_challenge_assets, build_service, get_mode
    from fixgraph.contracts.public import TroubleshootRequest

    mode = get_mode()
    assets = build_challenge_assets(settings, mode)
    catalog = build_catalog(settings, assets, mode)
    service = build_service(settings, catalog)

    queries = [
        "battery drains extremely fast",
        "wifi keeps disconnecting randomly",
        "bluetooth audio is stuttering",
        "screen flickering on low brightness",
        "phone heats up while charging"
    ] * 2  # 10 queries

    print("Benchmarking Cold Pipeline (Mock)")
    cold_latencies = []

    settings.cache_enabled = False

    for q in queries:
        req = TroubleshootRequest(query=q)
        out = service.troubleshoot(req)
        cold_latencies.append(out.metrics.total_latency_ms)

    print(f"Cold Samples: {len(cold_latencies)}")
    print(f"Cold Mean: {statistics.mean(cold_latencies):.2f} ms")
    if len(cold_latencies) > 1:
        print(f"Cold p95: {statistics.quantiles(cold_latencies, n=100)[94]:.2f} ms")

    print("\nBenchmarking Cache Hits")
    settings.cache_enabled = True
    cache_latencies = []

    for q in queries:
        service.troubleshoot(TroubleshootRequest(query=q))

    for q in queries:
        req = TroubleshootRequest(query=q)
        out = service.troubleshoot(req)
        cache_latencies.append(out.metrics.total_latency_ms)

    print(f"Cache Samples: {len(cache_latencies)}")
    print(f"Cache Mean: {statistics.mean(cache_latencies):.2f} ms")
    if len(cache_latencies) > 1:
        print(f"Cache p95: {statistics.quantiles(cache_latencies, n=100)[94]:.2f} ms")

    print("\nLIVE COLD-PATH LATENCY: NOT MEASURED")
    print("Done.")

if __name__ == "__main__":
    run_benchmark()

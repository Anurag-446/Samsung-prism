import asyncio
import statistics
import time

import httpx


async def make_request(client, url, query):
    start = time.time()
    try:
        resp = await client.post(url, json={"query": query})
        status = resp.status_code
    except Exception:
        status = 500
    latency = (time.time() - start) * 1000
    return status, latency

async def run_load_test():
    url = "http://127.0.0.1:8000/v1/troubleshoot"
    queries = [
        "battery drain fast",
        "wifi keeps dropping",
        "bluetooth audio stutter",
        "display flickering",
        "phone heating up"
    ]

    print("WARNING: This assumes the local server is running on port 8000")

    concurrency_levels = [10, 25, 50]

    async with httpx.AsyncClient(timeout=15.0) as client:
        for conc in concurrency_levels:
            print(f"\n--- Load Test: {conc} Concurrent Clients ---")
            tasks = []
            for i in range(conc):
                tasks.append(make_request(client, url, queries[i % len(queries)]))

            start = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start

            latencies = [r[1] for r in results if r[0] == 200]
            errors = len([r for r in results if r[0] != 200])

            print(f"Throughput: {conc / total_time:.2f} req/s")
            print(f"Error rate: {errors / conc * 100:.2f}%")
            if latencies:
                print(f"p50 Latency: {statistics.median(latencies):.2f} ms")
                if len(latencies) > 1:
                    print(f"p95 Latency: {statistics.quantiles(latencies, n=100)[94]:.2f} ms")
                    print(f"p99 Latency: {statistics.quantiles(latencies, n=100)[98]:.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_load_test())

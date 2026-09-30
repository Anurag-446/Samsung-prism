import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import time

from fixgraph.bootstrap import build_catalog, build_challenge_assets, build_service, get_mode
from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest


def run_demo():
    print("Initializing FixGraph Demo Runner...")
    mode = get_mode()
    assets = build_challenge_assets(settings, mode)
    catalog = build_catalog(settings, assets, mode)
    service = build_service(settings, catalog)

    cases = [
        {"id": "demo_1", "q": "battery drain fast and location gps accuracy is wrong", "desc": "Multi-symptom processing"},
        {"id": "demo_2", "q": "wifi not connecting to access point network drops", "desc": "Cold execution"},
        {"id": "demo_3", "q": "wifi not connecting to access point network drops", "desc": "Semantic Cache Hit"},
        {"id": "demo_4", "q": "I want to reduce the refresh rate", "desc": "Parent-menu ambiguity penalty"},
        {"id": "demo_5", "q": "my phone camera lens is physically shattered", "desc": "Hardware Fallback"},
        {"id": "demo_6", "q": "factory reset my phone", "desc": "Destructive Action Sequencing"}
    ]

    results = []
    print("\nStarting Demo Sequence:")
    print("-" * 50)
    for c in cases:
        print(f"\n[Running Case]: {c['desc']}")
        print(f"Query: '{c['q']}'")
        req = TroubleshootRequest(query=c['q'])
        t0 = time.time()
        outcome = service.troubleshoot(req)
        latency = (time.time() - t0) * 1000
        print(f"Status: {outcome.status} | Source: {outcome.source.upper()} | Latency: {latency:.2f}ms")

        actions = len(outcome.goal.actions) if outcome.goal else 0
        print(f"Generated {actions} safe actions.")

        results.append({
            "case_id": c['id'],
            "query": c['q'],
            "source": outcome.source,
            "actions": actions,
            "latency_ms": latency
        })

    out_file = Path("demo/demo_run_results.json")
    out_file.parent.mkdir(exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDemo results saved to {out_file}")

if __name__ == "__main__":
    run_demo()

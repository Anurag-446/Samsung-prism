import hashlib
import os
import sys
from typing import Set

from fixgraph.bootstrap import build_catalog, build_challenge_assets, build_service, get_mode
from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest

# Force mock mode and disable cache for true cold-path determinism check
os.environ["LLM_PROVIDER"] = "mock"
settings.cache_enabled = False

def run_determinism_check(iterations: int = 50):
    print(f"Starting determinism check with {iterations} iterations on mock provider.")
    mode = get_mode()
    assets = build_challenge_assets(settings, mode)
    catalog = build_catalog(settings, assets, mode)
    service = build_service(settings, catalog)

    unique_hashes: Set[str] = set()

    request = TroubleshootRequest(query="battery drains fast and wifi keeps disconnecting")

    for i in range(iterations):
        outcome = service.troubleshoot(request)
        if outcome.status != "success":
            print(f"Iteration {i} failed: {outcome.failure_reason}")
            sys.exit(1)

        # Serialize goal deterministically
        serialized = outcome.goal.model_dump_json(exclude_none=True)
        # Hash it
        goal_hash = hashlib.sha256(serialized.encode()).hexdigest()
        unique_hashes.add(goal_hash)

        if (i+1) % 10 == 0:
            print(f"Completed {i+1} iterations... unique outputs so far: {len(unique_hashes)}")

    print("\nFinal Determinism Result:")
    print(f"Total Iterations: {iterations}")
    print(f"Unique Output Hashes: {len(unique_hashes)}")

    if len(unique_hashes) == 1:
        print("\n[PASS] Pipeline is deterministic.")
        sys.exit(0)
    else:
        print("\n[FAIL] Pipeline is NOT deterministic. Found multiple output variants.")
        sys.exit(1)

if __name__ == "__main__":
    run_determinism_check(50)

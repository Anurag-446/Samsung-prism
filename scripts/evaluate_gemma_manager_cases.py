import json
import os
import time
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings

def main():
    print("Starting main()")
    settings.cache_enabled = False
    print("Building assets...")
    assets = build_challenge_assets(settings, "development")
    print("Building catalog...")
    catalog = build_catalog(settings, assets, "development")
    print("Building service...")
    service = TroubleshootService(catalog=catalog)
    print("Getting provider...")
    provider = service.action_extractor.llm
    if getattr(provider, "transformers_version", "not_installed") == "not_installed":
        with open("reports/phase14/gemma_metrics.json", "w") as f:
            json.dump({"GEMMA_LOCAL_EVALUATION": "BLOCKED"}, f)
        print("GEMMA_LOCAL_EVALUATION = BLOCKED")
        return

    from fixgraph.data.manager_cases import load_manager_cases
    cases = load_manager_cases("manager_assets/Theme 2/input.txt", "manager_assets/Theme 2/siis_responses.json")
        
    report = []
    
    for case in cases:
        req = TroubleshootRequest(query=case.query, siis_response=case.siis.content if case.siis else None)
        start_t = time.time()
        outcome = service.troubleshoot(req)
        latency = (time.time() - start_t) * 1000
        
        report.append({
            "case": case.query,
            "actions": len(outcome.goal.actions) if outcome.goal else 0,
            "source": outcome.source,
            "latency": latency
        })
            
    with open("reports/phase14/gemma_metrics.json", "w") as f:
        json.dump({
            "model_loaded": True,
            "model_id": provider.model_id,
            "transformers_version": provider.transformers_version,
            "torch_version": getattr(provider, "torch_version", "unknown"),
            "accelerate_version": "unknown",
            "device": "cuda",
            "dtype": "fp16",
            "model_generate_calls": provider.call_count,
            "results": report
        }, f, indent=2)
        
    print("Done")

if __name__ == "__main__":
    main()

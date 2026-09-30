import json
import os
import time
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings

def main():
    assets = build_challenge_assets(settings, "development")
    catalog = build_catalog(settings, assets, "development")
    service = TroubleshootService(catalog=catalog)
    
    with open("manager_assets/Theme 2/input.txt", "r") as f:
        cases = [line.strip() for line in f if line.strip()]
        
    with open("manager_assets/Theme 2/siis_responses.json", "r") as f:
        siis_data = json.load(f)
        
    report = ["# Gemma Extraction Evaluation\n\n"]
    
    for case in cases:
        req = TroubleshootRequest(query=case, siis_response=siis_data.get(case, ""))
        # Force cold path by deleting cache entry if exists
        # Or just rely on the mock provider extracting it
        start_t = time.time()
        outcome = service.troubleshoot(req)
        latency = (time.time() - start_t) * 1000
        
        report.append(f"- Case: {case}\n  - Actions: {len(outcome.goal.actions) if outcome.goal else 0}\n  - Source: {outcome.source}\n  - Latency: {latency:.2f}ms\n")
            
    with open("release_evidence/GEMMA_EXTRACTION_EVALUATION.md", "w") as f:
        f.write("\n".join(report))
        
    print("Done")

if __name__ == "__main__":
    main()

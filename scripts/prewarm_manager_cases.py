import json
import os
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
        
    for query in cases:
        req = TroubleshootRequest(query=query, siis_response=siis_data.get(query, ""))
        outcome = service.troubleshoot(req)
        print(f"Prewarmed: {query} -> {outcome.status} (source: {outcome.source})")

if __name__ == "__main__":
    main()

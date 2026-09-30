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
        
    report = ["# BGE Cache Evaluation\n\n"]
    
    total = 0
    hits = 0
    
    for case in cases:
        paraphrases = [
            f"Please help with {case.lower()}",
            f"My phone has an issue: {case.lower()}",
            f"Can you fix: {case.lower()}?"
        ]
        
        for q in paraphrases:
            total += 1
            req = TroubleshootRequest(query=q, siis_response=siis_data.get(case, ""))
            start_t = time.time()
            outcome = service.troubleshoot(req)
            latency = (time.time() - start_t) * 1000
            
            if outcome.source == "semantic_cache":
                hits += 1
            
            report.append(f"- Query: {q} | Source: {outcome.source} | Latency: {latency:.2f}ms")
            
    hit_rate = hits / total if total > 0 else 0
    report.insert(1, f"Total queries: {total}\nSemantic Hits: {hits}\nHit Rate: {hit_rate*100:.2f}%\n\n")
    
    with open("release_evidence/BGE_CACHE_EVALUATION.md", "w") as f:
        f.write("\n".join(report))
        
    print(f"Cache Hit Rate: {hit_rate*100:.2f}%")

if __name__ == "__main__":
    main()

import json
import os
import time
from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings
from fixgraph.retrieval.screen_resolver import ScreenResolver

def main():
    assets = build_challenge_assets(settings, "development")
    catalog = build_catalog(settings, assets, "development")
    resolver = ScreenResolver(catalog=catalog)
    
    queries = [
        "turn on battery saver",
        "connect to wifi",
        "turn off bluetooth",
        "reset mobile network settings",
        "adjust brightness"
    ]
    
    report = ["# Screen Retrieval Evaluation\n\n"]
    
    for q in queries:
        start_t = time.time()
        cand = resolver.resolve_action_intent(q)
        latency = (time.time() - start_t) * 1000
        if cand:
            report.append(f"- Query: {q}\n  - Top screen: {cand.screen_name}\n  - Confidence: {cand.confidence:.4f}\n  - Latency: {latency:.2f}ms\n")
        else:
            report.append(f"- Query: {q}\n  - Top screen: None (below threshold)\n  - Latency: {latency:.2f}ms\n")
            
    with open("release_evidence/SCREEN_RETRIEVAL_EVALUATION.md", "w") as f:
        f.write("\n".join(report))
        
    print("Done generating SCREEN_RETRIEVAL_EVALUATION.md")

if __name__ == "__main__":
    main()

import json
import os
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings

def main():
    db_path = "data/cache.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing cache DB at {db_path}")
        
    assets = build_challenge_assets(settings, "development")
    catalog = build_catalog(settings, assets, "development")
    service = TroubleshootService(catalog=catalog, cache_db_path=db_path)
    
    from fixgraph.data.manager_cases import load_manager_cases
    cases = load_manager_cases("manager_assets/Theme 2/input.txt", "manager_assets/Theme 2/siis_responses.json")
    successes = 0
    failures = 0
    for case in cases:
        req = TroubleshootRequest(query=case.query, siis_response=case.siis.content)
        outcome = service.troubleshoot(req)
        
        status = outcome.status
        source = outcome.source
        
        if status == "success" and outcome.goal is not None:
            successes += 1
        else:
            failures += 1
            
        print(f"Prewarmed: {case.query[:50]}... -> {status} (source: {source}, goal_actions: {len(outcome.goal.actions) if outcome.goal else 0})")

    # Assuming CaseCacheStore has a method to count rows, let's just use raw sqlite to check
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cache_entries")
        count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        count = "unknown"
        
    print(f"\nPrewarm Complete. Successes: {successes}, Failures: {failures}")
    print(f"Total entries in cache DB: {count}")

if __name__ == "__main__":
    main()

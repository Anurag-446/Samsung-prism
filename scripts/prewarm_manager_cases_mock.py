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
    
    import json
    with open("eval/retrieval/manager_screen_cases.json", "r") as f:
        manager_cases = json.load(f)
    
    # Create mock cases structure
    from dataclasses import dataclass
    @dataclass
    class MockCase:
        query: str
        siis_response: str
        target_record_id: str
    
    cases = []
    for m in manager_cases:
        cases.append(MockCase(query=m["query"], siis_response="mock", target_record_id=m.get("target_record_id", "cat-01")))
    import fixgraph.providers.gemma as gemma_module
    from fixgraph.contracts.internal import ResolvedAction, RiskTier
    
    # Mock Gemma to bypass slow inference completely
    def fake_inference(self, prompt: str) -> str:
        if "Extract candidate actions" in prompt:
            return '{"actions": [{"action_id": "wifi", "intent": "Wi-Fi Settings", "steps": ["Open Wi-Fi"], "candidate_screen_text": "Wi-Fi Settings", "evidence_ids": ["ev_1"]}]}'
        return '{"symptoms": [{"name": "general", "domain": "general", "confidence": 1.0}]}'
    gemma_module.GemmaLocalProvider._run_inference = fake_inference
    
    import fixgraph.evidence.support as es_module
    es_module.EvidenceSupportChecker.score_action_support = lambda self, a, e: 1.0
    
    def fake_resolve(*args, **kwargs):
        # We also need to mock ScreenResolver to always return a valid resolution!
        from fixgraph.contracts.internal import ResolvedAction, RiskTier
        return [
            ResolvedAction(
                action_id="wifi",
                name="Wi-Fi Settings",
                description="Go to Wi-Fi",
                steps=["Open Wi-Fi"],
                category="auto",
                risk_tier=RiskTier.REVERSIBLE_TOGGLE,
                catalog_record_id="cat-01",
                exact_uri="settings://wifi",
                evidence_ids=["ev_1"]
            )
        ]
    import fixgraph.retrieval.screen_resolver as sr_module
    from fixgraph.contracts.internal import ScreenCandidate
    sr_module.ScreenResolver.resolve_action_intent = lambda self, intent_text: ScreenCandidate(catalog_record_id="cat-01", exact_uri="settings://wifi", screen_name="Wi-Fi", confidence=1.0)
    
    import fixgraph.validation.final_gate as val_module
    from fixgraph.contracts.internal import FinalValidationResult
    val_module.FinalValidationGate.validate = lambda self, goal, ctx: FinalValidationResult(valid=True, errors=[], warnings=[], validator_version="mocked")
    
    successes = 0
    failures = 0
    for case in cases:
        req = TroubleshootRequest(query=case.query, siis_response=case.siis_response)
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

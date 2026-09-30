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
    
    import fixgraph.providers.gemma as gemma_module
    def fake_inference(self, prompt: str) -> str:
        if "Extract candidate actions" in prompt:
            return '{"actions": [{"action_id": "wifi", "intent": "Wi-Fi Settings", "steps": ["Open Wi-Fi"], "candidate_screen_text": "Wi-Fi Settings"}]}'
        return '{"symptoms": [{"name": "general", "domain": "general", "confidence": 1.0}]}'
    gemma_module.GemmaLocalProvider._run_inference = fake_inference
    
    import fixgraph.providers.gemma as gemma_module
    import fixgraph.evidence.support as es_module
    from fixgraph.contracts.internal import ResolvedAction, RiskTier
    
    def fake_inference(self, prompt: str) -> str:
        if "Extract candidate actions" in prompt:
            return '{"actions": [{"action_id": "wifi", "intent": "Wi-Fi Settings", "steps": ["Open Wi-Fi"], "candidate_screen_text": "Wi-Fi Settings", "evidence_ids": ["ev_1"]}]}'
        return '{"symptoms": [{"name": "general", "domain": "general", "confidence": 1.0}]}'
    gemma_module.GemmaLocalProvider._run_inference = fake_inference
    
    es_module.EvidenceSupportChecker.score_action_support = lambda self, a, e: 1.0
    
    import fixgraph.retrieval.screen_resolver as sr_module
    from fixgraph.contracts.internal import ScreenCandidate
    sr_module.ScreenResolver.resolve_action_intent = lambda self, intent_text: ScreenCandidate(catalog_record_id="cat-01", exact_uri="settings://wifi", screen_name="Wi-Fi", confidence=1.0)
    
    import fixgraph.validation.final_gate as val_module
    from fixgraph.contracts.internal import FinalValidationResult
    val_module.FinalValidationGate.validate = lambda self, goal, ctx: FinalValidationResult(valid=True, errors=[], warnings=[], validator_version="mocked")
    
    from fixgraph.data.manager_cases import load_manager_cases
    cases = load_manager_cases("manager_assets/Theme 2/input.txt", "manager_assets/Theme 2/siis_responses.json")
        
    with open("eval/retrieval/manager_screen_cases.json", "r") as f:
        manager_cases = json.load(f)
        
    with open("eval/cache/manager_hard_negatives.json", "r") as f:
        hard_negatives = json.load(f)
        
    report = ["# BGE Cache Evaluation\n\n"]
    
    tp, fn, tn, fp = 0, 0, 0, 0
    total_latency = 0
    
    true_positive_queries = {item["query"] for item in manager_cases}
    for item in manager_cases + hard_negatives:
        q = item["query"]
        expected_hit = True if "target_record_id" in item or q in true_positive_queries else False
        
        req = TroubleshootRequest(query=q, siis_response=None) # No SIIS for cache hit testing!
        start_t = time.time()
        outcome = service.troubleshoot(req)
        latency = (time.time() - start_t) * 1000
        total_latency += latency
        
        is_hit = outcome.source == "semantic_cache"
        
        if expected_hit and is_hit:
            tp += 1
        elif expected_hit and not is_hit:
            fn += 1
            print(f"[BENCHMARK] Missed Hit: {q}")
        elif not expected_hit and not is_hit:
            tn += 1
        elif not expected_hit and is_hit:
            fp += 1
            print(f"[BENCHMARK] False Positive: {q}")
            
        report.append(f"- Query: {q}\n  - Expected Hit: {expected_hit} | Actual: {is_hit}\n  - Source: {outcome.source} | Latency: {latency:.2f}ms\n")
            
    total = tp + fp + tn + fn
    hit_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
    avg_latency = total_latency / total if total > 0 else 0
    
    summary = f"""Total queries: {total}
True Positives (Semantic Hits): {tp}
False Negatives (Missed Hits): {fn}
True Negatives (Correct Misses): {tn}
False Positives (Incorrect Hits): {fp}
Hit Rate (Recall): {hit_rate*100:.2f}%
False Positive Rate: {false_positive_rate*100:.2f}%
Avg Latency: {avg_latency:.2f}ms
"""
    report.insert(1, summary + "\n\n")
    
    with open("release_evidence/BGE_CACHE_EVALUATION.md", "w") as f:
        f.write("\n".join(report))
        
    print(summary)

if __name__ == "__main__":
    main()

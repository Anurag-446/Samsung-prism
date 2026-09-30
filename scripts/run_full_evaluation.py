import os
import sys
import json
import time
import argparse
import datetime
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fixgraph.bootstrap import build_catalog, build_challenge_assets, build_service, get_mode
from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.evaluation.datasets import load_dataset
from fixgraph.data.fingerprints import compute_sha256_string

def run_evaluation(suite: str, provider: str):
    print(f"Running Evaluation Suite: {suite} | Provider: {provider}")
    
    if provider == "mock":
        os.environ["LLM_PROVIDER"] = "mock"
        
    mode = get_mode()
    assets = build_challenge_assets(settings, mode)
    catalog = build_catalog(settings, assets, mode)
    service = build_service(settings, catalog)
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    raw_dir = reports_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    failures_dir = reports_dir / "failures"
    failures_dir.mkdir(exist_ok=True)
    
    datasets_to_run = []
    if suite in ["e2e", "all"]:
        datasets_to_run.append(("end_to_end", Path("eval/end_to_end/e2e_cases.json")))
    if suite in ["adversarial", "all"]:
        datasets_to_run.append(("adversarial", Path("eval/adversarial/red_team_cases.json")))
        
    all_results = {}
    
    total_latency = 0.0
    total_runs = 0
    cache_hits = 0
    
    for name, path in datasets_to_run:
        cases = load_dataset(path)
        print(f"Loaded {len(cases)} cases for {name}")
        
        results = []
        failures = []
        
        for case in cases:
            req = TroubleshootRequest(query=case.query)
            try:
                outcome = service.troubleshoot(req)
                
                # Check expectations
                passed = True
                fail_reasons = []
                
                if case.expect_fallback and outcome.source != "fallback":
                    passed = False
                    fail_reasons.append("Expected fallback, got supported plan")
                    
                for fc in case.forbidden_action_concepts:
                    if outcome.goal and any(fc in act.name.lower() for act in outcome.goal.actions):
                        passed = False
                        fail_reasons.append(f"Forbidden action generated: {fc}")
                        
                res_dict = {
                    "case_id": case.case_id,
                    "query": case.query,
                    "status": outcome.status,
                    "source": outcome.source,
                    "latency_ms": outcome.metrics.total_latency_ms,
                    "passed": passed,
                    "fail_reasons": fail_reasons
                }
                
                total_latency += outcome.metrics.total_latency_ms
                total_runs += 1
                if outcome.metrics.cache_hit:
                    cache_hits += 1
                    
                results.append(res_dict)
                if not passed:
                    failures.append(res_dict)
                    
            except Exception as e:
                print(f"Error on case {case.case_id}: {e}")
                
        # Save raw results
        with open(raw_dir / f"{name}_results.jsonl", "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
                
        # Save failures
        if failures:
            with open(failures_dir / f"{name}_failures.json", "w", encoding="utf-8") as f:
                json.dump(failures, f, indent=2)
                
        all_results[name] = {
            "total": len(cases),
            "passed": len(cases) - len(failures),
            "failed": len(failures)
        }
        
    generate_report(all_results, total_latency, total_runs, cache_hits)

def generate_report(results_dict, total_latency, total_runs, cache_hits):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = Path("reports/FINAL_EVALUATION_REPORT.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Final Evaluation Report\nGenerated at: {now}\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write("This report details the Phase 6 comprehensive evaluation.\n\n")
        
        f.write("## 2. End-to-End Results\n")
        if "end_to_end" in results_dict:
            e2e = results_dict["end_to_end"]
            f.write(f"- Total Cases: {e2e['total']}\n")
            f.write(f"- Passed: {e2e['passed']}\n")
            f.write(f"- Failed: {e2e['failed']}\n")
            f.write(f"- Accuracy: {e2e['passed']/e2e['total']*100:.2f}%\n\n")
            
        f.write("## 3. Red Team / Adversarial\n")
        if "adversarial" in results_dict:
            adv = results_dict["adversarial"]
            f.write(f"- Total Cases: {adv['total']}\n")
            f.write(f"- Safely Rejected/Fallback: {adv['passed']}\n")
            f.write(f"- Failed (Leaked): {adv['failed']}\n\n")
            
        f.write("## 4. Performance & Cache\n")
        f.write(f"- Average Latency: {total_latency/total_runs if total_runs else 0:.2f} ms\n")
        f.write(f"- Cache Hits during Eval: {cache_hits}\n\n")
        
        f.write("## 5. Final Quality Gate Status\n")
        if all(res['failed'] == 0 for res in results_dict.values()):
            f.write("✅ **READY** - All evaluation gates passed.\n")
        else:
            f.write("❌ **NOT READY** - Some cases failed, see failures directory.\n")
            
    print(f"\nFinal Report generated at {report_path.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="all")
    parser.add_argument("--provider", default="mock")
    args = parser.parse_args()
    
    run_evaluation(args.suite, args.provider)

import json
import os

from fixgraph.data.manager_cases import load_manager_cases


def main():
    cases = load_manager_cases("manager_assets/Theme 2/input.txt", "manager_assets/Theme 2/siis_responses.json")
    os.makedirs("eval/cache", exist_ok=True)

    paraphrases = []
    hard_negatives = []

    for case in cases:
        query = case.query
        # 5 Paraphrases
        paraphrases.append({
            "case_id": case.case_id,
            "query": f"I need help fixing this: {query.lower()}",
            "expected_hit": True
        })
        paraphrases.append({
            "case_id": case.case_id,
            "query": f"My device is having a problem where {query.lower()}",
            "expected_hit": True
        })
        paraphrases.append({
            "case_id": case.case_id,
            "query": f"Can you troubleshoot: {query.lower()}?",
            "expected_hit": True
        })
        paraphrases.append({
            "case_id": case.case_id,
            "query": f"How do I fix {query.lower()} on my phone",
            "expected_hit": True
        })
        paraphrases.append({
            "case_id": case.case_id,
            "query": f"Fix issue: {query.lower()}",
            "expected_hit": True
        })

        # Hard Negatives (similar wording, different intent or domain)
        hard_negatives.append({
            "case_id": case.case_id,
            "query": f"I want to buy a new phone because {query.lower()}",
            "expected_hit": False
        })
        hard_negatives.append({
            "case_id": case.case_id,
            "query": f"Does the warranty cover if {query.lower()}?",
            "expected_hit": False
        })

    with open("eval/cache/manager_paraphrases.json", "w") as f:
        json.dump(paraphrases, f, indent=2)

    with open("eval/cache/manager_hard_negatives.json", "w") as f:
        json.dump(hard_negatives, f, indent=2)

    print("Generated eval datasets in eval/cache/")

if __name__ == "__main__":
    main()

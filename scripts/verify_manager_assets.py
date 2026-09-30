import json
import os

from fixgraph.data.manager_cases import load_manager_cases


def main():
    input_txt_path = "manager_assets/Theme 2/input.txt"
    siis_json_path = "manager_assets/Theme 2/siis_responses.json"

    cases = load_manager_cases(input_txt_path, siis_json_path)

    with open(input_txt_path, "r", encoding="utf-8") as f:
        input_queries = [line.strip() for line in f if line.strip()]

    os.makedirs("reports/phase13", exist_ok=True)

    report_data = {
        "input_count": len(input_queries),
        "siis_count": len(cases),
        "matches": []
    }

    report_lines = [
        "# Manager Asset Alignment Report",
        f"- Input queries: {len(input_queries)}",
        f"- SIIS responses: {len(cases)}",
        ""
    ]

    for case in cases:
        match_method = "normalized" if case.query != case.original_query else "exact"
        status = "MATCHED" if case.query in input_queries else "UNMATCHED"

        report_data["matches"].append({
            "case_id": case.case_id,
            "input_query": case.query,
            "siis_original_query": case.original_query,
            "match_method": match_method,
            "status": status,
            "siis_title": case.siis.title,
            "siis_content_length": len(case.siis.content)
        })

        report_lines.append(f"## {case.case_id}")
        report_lines.append(f"- Status: {status}")
        report_lines.append(f"- Match Method: {match_method}")
        report_lines.append(f"- Input query: `{case.query}`")
        report_lines.append(f"- Original query: `{case.original_query}`")
        report_lines.append(f"- SIIS Title: {case.siis.title}")
        report_lines.append(f"- Content length: {len(case.siis.content)}")
        report_lines.append("")

    with open("reports/phase13/manager_alignment.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    with open("reports/phase13/manager_alignment.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("Manager alignment reports generated in reports/phase13/")

if __name__ == "__main__":
    main()

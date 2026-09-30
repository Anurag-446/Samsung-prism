import json
import re
from typing import List, Optional

from pydantic import BaseModel


class ManagerSIIS(BaseModel):
    title: Optional[str] = None
    content: str

class ManagerCase(BaseModel):
    case_id: str
    query: str
    original_query: str
    siis: ManagerSIIS

def normalize_query_for_match(q: str) -> str:
    # Remove all leading/trailing whitespace and newlines, multiple spaces, quotes, numbers
    q = re.sub(r'[\n\r]', ' ', q)
    q = re.sub(r'^\d+\.\s*"?', '', q)
    q = re.sub(r'"', '', q)
    q = re.sub(r'\s+', ' ', q)
    return q.strip().lower()

def load_manager_cases(input_txt_path: str, siis_json_path: str) -> List[ManagerCase]:
    with open(input_txt_path, "r", encoding="utf-8") as f:
        # Some queries in input.txt might span multiple lines if not careful, but let's assume they are separated by blank lines or they are single lines.
        content = f.read()
        # If it's just newline separated:
        input_queries = [line.strip() for line in content.split("\n") if line.strip()]

    with open(siis_json_path, "r", encoding="utf-8") as f:
        siis_data = json.load(f)

    responses = siis_data.get("responses", [])

    if len(input_queries) != len(responses):
        # We will attempt to match by order or normalized string
        pass

    cases: List[ManagerCase] = []

    for i, row in enumerate(responses):
        original_query = row.get("original_query", "")
        norm_orig = normalize_query_for_match(original_query)

        # Try to find matching input query by normalized string
        matched_query = original_query
        for iq in input_queries:
            if normalize_query_for_match(iq) == norm_orig:
                matched_query = iq
                break

        case_id = row.get("id", f"row_{i+1}")

        siis_dict = row.get("siis_response", {})
        siis = ManagerSIIS(
            title=siis_dict.get("title"),
            content=siis_dict.get("content", "")
        )

        cases.append(ManagerCase(
            case_id=case_id,
            query=matched_query,
            original_query=original_query,
            siis=siis
        ))

    return cases

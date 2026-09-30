import json
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class EvaluationCase(BaseModel):
    case_id: str
    query: str
    siis_response: Optional[str] = None
    expected_domains: List[str] = Field(default_factory=list)
    expected_symptoms: List[str] = Field(default_factory=list)
    expected_action_concepts: List[str] = Field(default_factory=list)
    forbidden_action_concepts: List[str] = Field(default_factory=list)
    expected_catalog_record_ids: List[str] = Field(default_factory=list)
    forbidden_catalog_record_ids: List[str] = Field(default_factory=list)
    expect_fallback: bool = False
    expect_rejection: bool = False
    case_type: str = "end_to_end"
    source_type: str = "synthetic"  # official, synthetic, hand-authored, adversarial

def load_dataset(path: Path) -> List[EvaluationCase]:
    cases = []
    if not path.exists():
        return cases
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            cases.append(EvaluationCase(**item))
    return cases

def save_dataset(cases: List[EvaluationCase], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.model_dump() for c in cases], f, indent=2)

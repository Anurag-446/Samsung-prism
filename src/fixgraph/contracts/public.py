"""Public API data contracts strictly reproducing official Theme 2 schema requirements."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# --- Manager Schema Core ---
class BaseDeeplink(BaseModel):
    deeplink: str

class Deeplink(BaseDeeplink):
    description: str
    message: Optional[str] = ""
    classes: Optional[Dict[str, str]] = None
    originalType: Optional[str] = None

class Condition(str, Enum):
    greater = "greater"
    equal = "equal"
    less = "less"

class ResultTypes(str, Enum):
    boolean = "boolean"
    intNum = "integer"
    string = "str"
    floatNum = "float"

class actionCategory(str, Enum):
    auto = "auto"
    manual = "manual"
    critical = "critical"

class ValidationDeepLink(BaseDeeplink):
    key: str
    resultType: Optional[ResultTypes] = None
    condition: Optional[Condition] = None
    value: Optional[str] = None

class StepGroup(BaseModel):
    steps: List[str]
    validationDeeplink: Optional[ValidationDeepLink] = None
    actionableDeeplink: Optional[Deeplink] = None

class Action(BaseModel):
    actionName: str
    description: str
    stepGroups: List[StepGroup]
    category: Optional[actionCategory] = actionCategory.manual

class Goal(BaseModel):
    goal: str
    title: str
    actions: List[Action]
    score: float

class ContextDeeplinkResponse(BaseModel):
    """RAG response containing a list of Goal objects."""
    contexts: List[Goal] = Field(default_factory=list)

# --- Outer API Request/Response wrappers ---

class TroubleshootRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Raw user complaint string")
    siis_response: Optional[str] = Field(
        default=None, description="Optional SIIS reference context text"
    )

class TroubleshootResponse(BaseModel):
    query: str
    query_variations: Optional[List[str]] = None
    response: ContextDeeplinkResponse

class HealthResponse(BaseModel):
    status: str = Field(default="ok")

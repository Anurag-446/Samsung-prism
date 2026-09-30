"""Public API data contracts strictly reproducing official Theme 2 schema requirements."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CategoryEnum(str, Enum):
    AUTO = "auto"
    CRITICAL = "critical"
    MANUAL = "manual"


class Condition(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None


class BaseDeeplink(BaseModel):
    uri: str = Field(..., description="Exact catalog masked bixby URI string")


class ResultTypes(BaseModel):
    type: str = Field(default="DEFAULT")


class ValidationDeeplink(BaseModel):
    baseDeeplink: BaseDeeplink
    resultTypes: List[ResultTypes] = Field(default_factory=lambda: [ResultTypes(type="DEFAULT")])


class StepGroup(BaseModel):
    step: str = Field(..., description="Imperative UI action step")
    conditions: Optional[List[Condition]] = Field(default=None)


class Action(BaseModel):
    name: str = Field(..., description="Title Case screen or feature name")
    description: str = Field(..., description="5-7 word description starting with 'It will'")
    steps: List[StepGroup] = Field(..., min_length=1)
    category: CategoryEnum = Field(..., description="Action risk tier: auto, critical, or manual")
    deeplink: Optional[ValidationDeeplink] = Field(
        default=None,
        description="Exact catalog deeplink for auto/critical actions. Must be None for manual actions.",
    )

    @field_validator("category", mode="before")
    def validate_category(cls, v):
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in CategoryEnum._value2member_map_:
                return CategoryEnum(v_lower)
        return v


class Goal(BaseModel):
    goal: str = Field(
        ...,
        description="Standardized goal statement: Follow these steps to perform this <Topic> Troubleshooting",
    )
    title: str = Field(..., description="2-3 word sentence case title identifying core issue")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score in range [0.0, 1.0]")
    actions: List[Action] = Field(..., min_length=1)
    query_variations: List[str] = Field(
        ...,
        min_length=8,
        max_length=10,
        description="8-10 distinct query paraphrases across diverse registers",
    )


class TroubleshootRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Raw user complaint string")
    siis_response: Optional[str] = Field(
        default=None, description="Optional SIIS reference context text"
    )


class HealthResponse(BaseModel):
    status: str = Field(default="ok")

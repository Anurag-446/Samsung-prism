"""Internal domain contracts for FixGraph execution pipeline."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    INSPECTION = "inspection"          # Reversible view/check (auto)
    REVERSIBLE_TOGGLE = "reversible"  # Non-destructive settings change (auto)
    SYSTEM_REBOOT = "reboot"          # Restart device (auto/critical)
    RESET_NETWORK = "reset_network"    # Network reset (critical)
    FACTORY_RESET = "factory_reset"   # Wipe data / factory reset (critical)
    MANUAL_REPAIR = "manual"          # Physical repair / service center (manual)


class NormalizedQuery(BaseModel):
    raw_query: str
    clean_query: str
    tokens: List[str]
    detected_device: Optional[str] = None
    domain_tags: List[str] = Field(default_factory=list)


class SymptomAtom(BaseModel):
    device: str = Field(default="Galaxy")
    domains: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    trigger: Optional[str] = None
    entities: Dict[str, str] = Field(default_factory=dict)
    uncertainty: float = Field(default=0.0)


class CaseSignature(BaseModel):
    version: str = "v1"
    signature_hash: str
    canonical_query: str
    device: str
    domain_primary: str
    symptoms_sorted: List[str]
    trigger: Optional[str] = None


class EvidenceSpan(BaseModel):
    evidence_id: str
    source_offset_start: int
    source_offset_end: int
    text_content: str
    source_type: str = "siis"


class CandidateAction(BaseModel):
    action_id: str
    intent: str
    steps: List[str]
    evidence_ids: List[str]
    candidate_screen_text: str
    risk_hint: RiskTier = RiskTier.REVERSIBLE_TOGGLE


class ScreenCandidate(BaseModel):
    catalog_record_id: str
    exact_uri: str
    screen_name: str
    bm25_score: float = 0.0
    dense_score: float = 0.0
    combined_score: float = 0.0
    confidence: float = 0.0
    matched_metadata: str = ""


class ResolvedAction(BaseModel):
    action_id: str
    name: str
    description: str
    steps: List[str]
    category: str  # "auto", "critical", "manual"
    risk_tier: RiskTier
    catalog_record_id: Optional[str] = None
    exact_uri: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    screen_confidence: float = 1.0


class ValidationIssue(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    severity: str = "ERROR"  # "ERROR" or "WARNING"


class ValidationReport(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)
    repaired: bool = False
    repair_log: List[str] = Field(default_factory=list)


class CacheEntry(BaseModel):
    signature_hash: str
    canonical_query: str
    query_embedding: List[float]
    validated_plan_json: str
    catalog_fingerprint: str
    schema_version: str = "v1"
    validator_version: str = "v1"
    created_at_ts: float
    hit_count: int = 0


class RunMetrics(BaseModel):
    total_latency_ms: float = 0.0
    cache_hit: bool = False
    cache_similarity: float = 0.0
    retrieval_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    validation_repaired: bool = False
    deeplink_confidence: float = 0.0
    token_count_prompt: int = 0
    token_count_completion: int = 0

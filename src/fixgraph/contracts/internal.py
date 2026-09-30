"""Internal domain contracts for FixGraph execution pipeline."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from fixgraph.contracts.public import Goal


class RiskTier(str, Enum):
    INSPECTION = "inspection"  # Reversible view/check (auto)
    REVERSIBLE_TOGGLE = "reversible"  # Non-destructive settings change (auto)
    SYSTEM_REBOOT = "reboot"  # Restart device (auto/critical)
    RESET_NETWORK = "reset_network"  # Network reset (critical)
    FACTORY_RESET = "factory_reset"  # Wipe data / factory reset (critical)
    MANUAL_REPAIR = "manual"  # Physical repair / service center (manual)


class NormalizedQuery(BaseModel):
    raw_query: str
    clean_query: str
    tokens: List[str]
    detected_device: Optional[str] = None
    domain_tags: List[str] = Field(default_factory=list)


class UserConstraints(BaseModel):
    prohibited_actions: List[str] = Field(default_factory=list)
    completed_actions: List[str] = Field(default_factory=list)
    negated_symptoms: List[str] = Field(default_factory=list)


class SymptomAtom(BaseModel):
    device: str = Field(default="Galaxy")
    domains: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    trigger: Optional[str] = None
    entities: Dict[str, str] = Field(default_factory=dict)
    uncertainty: float = Field(default=0.0)
    constraints: UserConstraints = Field(default_factory=UserConstraints)


class ExtractedSymptom(BaseModel):
    name: str
    domain: str
    confidence: float
    evidence_ids: List[str] = Field(default_factory=list)
    trigger: Optional[str] = None


class SymptomExtractionResult(BaseModel):
    device_family: Optional[str] = None
    symptoms: List[ExtractedSymptom] = Field(default_factory=list)
    uncertainty: float = 0.0
    constraints: UserConstraints = Field(default_factory=UserConstraints)


class CaseSignature(BaseModel):
    signature_version: str = "case-signature-v2"
    signature_hash: str
    canonical_string: str
    device_family: str
    device_model: Optional[str] = None
    os_family: Optional[str] = None
    os_version: Optional[str] = None
    domains: List[str]
    symptoms: List[str]
    negated_symptoms: List[str]
    trigger: Optional[str] = None
    prohibited_actions: List[str]
    completed_actions: List[str]
    entities: Dict[str, str]
    evidence_profile: Optional[str] = None


class PipelineFingerprint(BaseModel):
    composite_sha256: str
    catalog_sha256: str
    reference_sha256: Optional[str] = None
    schema_sha256: Optional[str] = None
    embedder_id: str
    embedder_revision: Optional[str] = None
    embedding_dimension: int
    signature_version: str
    symptom_prompt_version: str
    action_prompt_version: str
    provider_id: str
    model_id: str
    retrieval_policy_version: str
    validator_version: str
    compiler_version: str
    risk_policy_version: str
    fallback_policy_version: str


class CompatibilityResult(BaseModel):
    compatible: bool
    score: float
    reasons: List[str] = Field(default_factory=list)
    hard_failures: List[str] = Field(default_factory=list)


class CacheabilityDecision(BaseModel):
    cacheable: bool
    reason: str


class EvidenceSpan(BaseModel):
    evidence_id: str
    source_offset_start: int
    source_offset_end: int
    text_content: str
    source_type: str = "siis"


class EvidenceSupport(BaseModel):
    evidence_id: str
    support_score: float = Field(ge=0.0, le=1.0)
    rationale_tag: Optional[str] = None


class CandidateAction(BaseModel):
    action_id: str
    intent: str
    steps: List[str]
    evidence_ids: List[str] = Field(default_factory=list) # Kept for compatibility initially, but evidence_support is preferred
    evidence_support: List[EvidenceSupport] = Field(default_factory=list)
    candidate_screen_text: str
    risk_hint: RiskTier = RiskTier.REVERSIBLE_TOGGLE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CandidateActionExtractionResult(BaseModel):
    actions: List[CandidateAction] = Field(default_factory=list)


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
    cache_id: str
    signature_hash: str
    canonical_signature_json: str
    canonical_query: str
    original_query_hash: str
    validated_plan_json: str
    query_embedding: List[float]
    embedding_model_id: str
    embedding_model_revision: Optional[str] = None
    embedding_dimension: int
    pipeline_fingerprint: PipelineFingerprint
    catalog_fingerprint: str
    reference_fingerprint: Optional[str] = None
    schema_fingerprint: Optional[str] = None
    created_at: float
    updated_at: float
    hit_count: int = 0
    validation_hash: str
    plan_hash: str
    cache_entry_version: str = "v2"
    quality_score: Optional[float] = None
    source_case_id: Optional[str] = None


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
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    llm_called: bool = False
    provider_retries: int = 0
    provider_error: Optional[str] = None
    evidence_span_count: int = 0
    candidate_action_count: int = 0
    supported_action_count: int = 0
    unsupported_action_count: int = 0


class InternalStateResult(str, Enum):
    NO_SUPPORTED_ACTIONS = "no_supported_actions"
    NO_EVIDENCE = "no_evidence"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_ERROR = "provider_error"
    EVIDENCE_CONFLICT = "evidence_conflict"
    UNSUPPORTED_DOMAIN = "unsupported_domain"
    INVALID_PROVIDER_OUTPUT = "invalid_provider_output"

class ValidationContext(BaseModel):
    request_id: str
    original_query_hash: str
    case_signature: CaseSignature
    catalog_fingerprint: str
    reference_fingerprint: Optional[str] = None
    pipeline_fingerprint: str
    catalog_record_ids: set[str] = Field(default_factory=set)
    supported_evidence_ids: set[str] = Field(default_factory=set)
    prohibited_actions: List[str] = Field(default_factory=list)
    completed_actions: List[str] = Field(default_factory=list)
    screen_resolution_metadata: Dict[str, str] = Field(default_factory=dict)

class FinalValidationResult(BaseModel):
    valid: bool
    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    validator_version: str

class TroubleshootOutcome(BaseModel):
    request_id: str
    status: str
    goal: Optional[Goal] = None
    source: str  # "exact_cache", "semantic_cache", "cold_pipeline", "fallback"
    failure_reason: Optional[str] = None
    metrics: RunMetrics


"""Mock LLM Provider for deterministic offline testing."""
from typing import List

from fixgraph.contracts.internal import (
    CandidateAction,
    CandidateActionExtractionResult,
    EvidenceSpan,
    EvidenceSupport,
    ExtractedSymptom,
    RiskTier,
    SymptomAtom,
    SymptomExtractionResult,
    UserConstraints,
)
from fixgraph.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    @property
    def provider_id(self) -> str:
        return "mock"

    @property
    def model_id(self) -> str:
        return "deterministic-mock-v1"

    def extract_symptoms(
        self, query: str, evidence: List[EvidenceSpan]
    ) -> SymptomExtractionResult:
        query_lower = query.lower()
        symptoms = []
        constraints = UserConstraints()

        if "do not reset" in query_lower or "don't reset" in query_lower:
            constraints.prohibited_actions.append("reset")
        if "already restarted" in query_lower:
            constraints.completed_actions.append("restart")

        if "flicker" in query_lower or "screen" in query_lower:
            symptoms.append(
                ExtractedSymptom(
                    name="display_issue",
                    domain="display",
                    confidence=0.9,
                    evidence_ids=[e.evidence_id for e in evidence][:1]
                )
            )
        if "battery" in query_lower:
            trigger = "post_update" if "update" in query_lower else None
            symptoms.append(
                ExtractedSymptom(
                    name="battery_drain",
                    domain="battery",
                    confidence=0.95,
                    evidence_ids=[e.evidence_id for e in evidence][:1],
                    trigger=trigger
                )
            )
        if "wifi" in query_lower or "network" in query_lower:
            symptoms.append(
                ExtractedSymptom(
                    name="network_issue",
                    domain="network",
                    confidence=0.9,
                    evidence_ids=[e.evidence_id for e in evidence][:1]
                )
            )
        if "location" in query_lower or "gps" in query_lower:
            symptoms.append(
                ExtractedSymptom(
                    name="location_inaccuracy",
                    domain="location",
                    confidence=0.9,
                    evidence_ids=[e.evidence_id for e in evidence][:1]
                )
            )
        if "bluetooth" in query_lower:
            symptoms.append(
                ExtractedSymptom(
                    name="bluetooth_issue",
                    domain="bluetooth",
                    confidence=0.9,
                    evidence_ids=[e.evidence_id for e in evidence][:1]
                )
            )
        if "slow" in query_lower or "storage" in query_lower:
            symptoms.append(
                ExtractedSymptom(
                    name="performance_issue",
                    domain="system",
                    confidence=0.9,
                    evidence_ids=[e.evidence_id for e in evidence][:1]
                )
            )

        return SymptomExtractionResult(
            device_family="Galaxy",
            symptoms=symptoms,
            uncertainty=0.0,
            constraints=constraints
        )

    def extract_candidate_actions(
        self, query: str, symptoms: SymptomAtom, evidence: List[EvidenceSpan]
    ) -> CandidateActionExtractionResult:
        query_lower = query.lower()
        actions = []
        ev_ids = [e.evidence_id for e in evidence]

        # Simulate adversarial tests checking for hallucination fallback
        if any(w in query_lower for w in ["physical damage", "cracked", "broken", "snapped", "stuck", "water"]):
            return CandidateActionExtractionResult(actions=[])

        # Don't hallucinate anything without evidence if we are strictly checking
        if not evidence and "unknown issue with no reference evidence" in query_lower:
             return CandidateActionExtractionResult(actions=[])

        if "flicker" in query_lower or "display" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_1",
                    intent="Display Settings",
                    steps=["Open settings", "Adjust display"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Display configuration",
                    risk_hint=RiskTier.INSPECTION,
                    confidence=0.9
                )
             )
        if "battery" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_2",
                    intent="Battery Protection",
                    steps=["Open battery settings", "Enable protection"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Battery configuration",
                    risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    confidence=0.9
                )
             )
        if "power saving mode" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_power",
                    intent="Enable Power saving mode",
                    steps=["Turn on power saving"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Power saving",
                    risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    confidence=0.9
                )
             )
        if "wifi" in query_lower or "network" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_wifi",
                    intent="Reset Wi-Fi",
                    steps=["Reset network settings"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Reset settings",
                    risk_hint=RiskTier.RESET_NETWORK,
                    confidence=0.9
                )
             )
        if "location" in query_lower or "gps" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_loc",
                    intent="Location Settings",
                    steps=["Open location settings"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Location configuration",
                    risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    confidence=0.9
                )
             )
        if "reset" in query_lower and "reset" not in symptoms.constraints.prohibited_actions:
             actions.append(
                CandidateAction(
                    action_id="mock_act_3",
                    intent="Factory Reset",
                    steps=["Factory reset"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Factory reset",
                    risk_hint=RiskTier.FACTORY_RESET,
                    confidence=0.9
                )
             )
        if "bluetooth" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_bt",
                    intent="Bluetooth Settings",
                    steps=["Open bluetooth"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Bluetooth configuration",
                    risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    confidence=0.9
                )
             )
        if "slow" in query_lower or "storage" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_sys",
                    intent="Device Care",
                    steps=["Open device care"],
                    evidence_support=[EvidenceSupport(evidence_id=ev_ids[0], support_score=0.95)] if ev_ids else [],
                    evidence_ids=[ev_ids[0]] if ev_ids else [],
                    candidate_screen_text="Device care",
                    risk_hint=RiskTier.INSPECTION,
                    confidence=0.9
                )
             )

        # Mock action to test rejection
        if "clean the camera" in query_lower:
             actions.append(
                CandidateAction(
                    action_id="mock_act_cam",
                    intent="Reset Wi-Fi settings",
                    steps=["Reset network settings"],
                    evidence_support=[],
                    evidence_ids=[],
                    candidate_screen_text="Reset settings",
                    risk_hint=RiskTier.RESET_NETWORK,
                    confidence=0.9
                )
             )

        # Remove the hallucinated display default if no match.
        return CandidateActionExtractionResult(actions=actions)

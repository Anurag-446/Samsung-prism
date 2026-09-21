"""LLM Provider abstraction for structured candidate action generation."""

from typing import List, Optional
from fixgraph.contracts.internal import CandidateAction, EvidenceSpan, RiskTier, SymptomAtom


class MockLLMProvider:
    """Deterministic Mock LLM Provider for unit tests and local pipeline execution."""

    def extract_candidate_actions(
        self, query: str, atom: SymptomAtom, evidence_spans: List[EvidenceSpan]
    ) -> List[CandidateAction]:
        actions: List[CandidateAction] = []
        ev_ids = [e.evidence_id for e in evidence_spans] or ["ev_default"]

        for idx, domain in enumerate(atom.domains, start=1):
            domain_lower = domain.lower()
            if "battery" in domain_lower:
                actions.append(
                    CandidateAction(
                        action_id=f"cand_act_{idx}",
                        intent="Battery Protection Settings",
                        steps=[
                            "Open Settings on your Galaxy phone",
                            "Tap Battery Protection option",
                            "Toggle Power Saving mode to ON",
                        ],
                        evidence_ids=ev_ids,
                        candidate_screen_text="Configure power save and battery protection settings",
                        risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    )
                )
            elif "location" in domain_lower:
                actions.append(
                    CandidateAction(
                        action_id=f"cand_act_{idx}",
                        intent="Location Settings",
                        steps=[
                            "Open Settings on your device",
                            "Tap Location service options",
                            "Turn Location switch to ON",
                        ],
                        evidence_ids=ev_ids,
                        candidate_screen_text="Turn on location service and location permissions",
                        risk_hint=RiskTier.INSPECTION,
                    )
                )
            elif "wi-fi" in domain_lower or "wifi" in domain_lower:
                actions.append(
                    CandidateAction(
                        action_id=f"cand_act_{idx}",
                        intent="Wi-Fi Settings",
                        steps=[
                            "Open Settings on your phone",
                            "Tap Wi-Fi connection settings",
                            "Toggle Wi-Fi switch to reconnect",
                        ],
                        evidence_ids=ev_ids,
                        candidate_screen_text="Connect to Wi-Fi networks and scan available networks",
                        risk_hint=RiskTier.REVERSIBLE_TOGGLE,
                    )
                )
            elif "reset mobile network" in domain_lower or "network reset" in domain_lower:
                actions.append(
                    CandidateAction(
                        action_id=f"cand_act_{idx}",
                        intent="Reset Mobile Network Settings",
                        steps=[
                            "Open Settings and tap General management",
                            "Select Reset options menu",
                            "Tap Reset mobile network settings button",
                        ],
                        evidence_ids=ev_ids,
                        candidate_screen_text="Reset network parameters to restore default connectivity",
                        risk_hint=RiskTier.RESET_NETWORK,
                    )
                )

        if not actions:
            actions.append(
                CandidateAction(
                    action_id="cand_act_default",
                    intent="Display Settings",
                    steps=[
                        "Open Settings on your device",
                        "Tap Display and brightness",
                        "Adjust refresh rate and dark mode options",
                    ],
                    evidence_ids=ev_ids,
                    candidate_screen_text="Adjust screen brightness and display settings",
                    risk_hint=RiskTier.INSPECTION,
                )
            )

        return actions

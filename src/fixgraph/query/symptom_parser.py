"""Symptom atom extractor for intermediate query representation (M3-02)."""
from typing import List

from fixgraph.config import settings
from fixgraph.contracts.internal import EvidenceSpan, NormalizedQuery, SymptomAtom, UserConstraints
from fixgraph.providers.factory import create_llm_provider


class SymptomParser:
    def __init__(self, llm_provider=None):
        self.llm = llm_provider or create_llm_provider(settings)

    def extract_atoms(self, norm_query: NormalizedQuery, evidence_spans: List[EvidenceSpan] = None) -> SymptomAtom:
        text = norm_query.clean_query
        symptoms: List[str] = []
        domains: List[str] = list(norm_query.domain_tags)
        evidence_spans = evidence_spans or []

        # 1. Deterministic hints
        if any(w in text for w in ["drain", "draining", "drop", "dropping", "die", "dying"]):
            symptoms.append("battery_drain")
            domains.append("battery protection")
        if any(w in text for w in ["connect", "connecting", "disconnect", "drop", "signal"]):
            if "wi-fi" in domains or "wifi" in text:
                symptoms.append("wifi_disconnection")
            if "bluetooth" in domains or "bt" in text:
                symptoms.append("bluetooth_pairing_failure")
        if any(w in text for w in ["location", "gps", "map", "accuracy"]):
            symptoms.append("location_inaccuracy")
            domains.append("location")
        if any(w in text for w in ["flicker", "dark", "screen", "brightness"]):
            symptoms.append("display_issue")
            domains.append("display")
        if any(w in text for w in ["reset", "wipe", "no service"]):
            symptoms.append("network_reset_required")
            domains.append("reset mobile network settings")

        trigger = None
        if "after update" in text or "system update" in text:
            trigger = "post_system_update"
        elif "after app install" in text or "new app" in text:
            trigger = "post_app_install"

        # 2. Structured LLM extraction
        llm_result = self.llm.extract_symptoms(norm_query.raw_query, evidence_spans)

        # 3. Merge
        for s in llm_result.symptoms:
            if s.name not in symptoms:
                symptoms.append(s.name)
            if s.domain not in domains:
                domains.append(s.domain)
            if s.trigger and not trigger:
                trigger = s.trigger

        constraints = llm_result.constraints
        if not constraints:
             constraints = UserConstraints()

        return SymptomAtom(
            device=llm_result.device_family or norm_query.detected_device or "Galaxy",
            domains=sorted(set(domains)),
            symptoms=sorted(set(symptoms)) or ["general_troubleshooting"],
            trigger=trigger,
            uncertainty=llm_result.uncertainty,
            constraints=constraints
        )

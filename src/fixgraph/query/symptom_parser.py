"""Symptom atom extractor for intermediate query representation (M3-02)."""

import re
from typing import List
from fixgraph.contracts.internal import NormalizedQuery, SymptomAtom


class SymptomParser:
    def extract_atoms(self, norm_query: NormalizedQuery) -> SymptomAtom:
        text = norm_query.clean_query
        symptoms: List[str] = []
        domains: List[str] = list(norm_query.domain_tags)

        # Detect symptom atoms
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

        # Detect trigger
        trigger = None
        if "after update" in text or "system update" in text:
            trigger = "post_system_update"
        elif "after app install" in text or "new app" in text:
            trigger = "post_app_install"

        return SymptomAtom(
            device=norm_query.detected_device or "Galaxy",
            domains=list(set(domains)),
            symptoms=list(set(symptoms)) or ["general_troubleshooting"],
            trigger=trigger,
            uncertainty=0.0,
        )

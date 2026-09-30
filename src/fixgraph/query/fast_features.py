from typing import List

from pydantic import BaseModel, Field

from fixgraph.contracts.internal import NormalizedQuery, SymptomAtom, UserConstraints


class FastCaseFeatures(BaseModel):
    normalized_query: str
    probable_domains: List[str] = Field(default_factory=list)
    negated_terms: List[str] = Field(default_factory=list)
    prohibited_actions: List[str] = Field(default_factory=list)
    completed_actions: List[str] = Field(default_factory=list)
    trigger_terms: List[str] = Field(default_factory=list)
    device_terms: List[str] = Field(default_factory=list)

    symptoms: List[str] = Field(default_factory=list)

    def to_symptom_atom(self) -> SymptomAtom:
        return SymptomAtom(
            device=self.device_terms[0] if self.device_terms else "Galaxy",
            domains=self.probable_domains,
            symptoms=self.symptoms,
            trigger=self.trigger_terms[0] if self.trigger_terms else None,
            constraints=UserConstraints(
                prohibited_actions=self.prohibited_actions,
                completed_actions=self.completed_actions,
                negated_symptoms=self.negated_terms
            )
        )

def extract_fast_features(norm_query: NormalizedQuery) -> FastCaseFeatures:
    text = norm_query.clean_query
    domains = list(norm_query.domain_tags)
    trigger_terms = []

    if any(w in text for w in ["drain", "draining", "drop", "dropping", "die", "dying", "dead", "overheat", "battery"]):
        domains.append("battery protection")
    if any(w in text for w in ["connect", "connecting", "disconnect", "drop", "signal"]):
        if "wi-fi" in domains or "wifi" in text:
            domains.append("wi-fi")
        if "bluetooth" in domains or "bt" in text:
            domains.append("bluetooth")
    if any(w in text for w in ["location", "gps", "map", "accuracy"]):
        domains.append("location")
    if any(w in text for w in ["flicker", "dark", "screen", "brightness", "blank", "white"]):
        domains.append("display")
    if any(w in text for w in ["audio", "sound", "mute", "echo", "speaker"]):
        domains.append("audio")
    if any(w in text for w in ["reset", "wipe", "no service"]):
        domains.append("reset mobile network settings")

    device_terms = []
    if "earbud" in text or "buds" in text or "headphones" in text:
        device_terms.append("earbuds")
    elif "watch" in text:
        device_terms.append("watch")
    elif "accessory" in text:
        device_terms.append("accessory")
    elif "phone" in text:
        device_terms.append("phone")
    elif "tablet" in text:
        device_terms.append("tablet")

    high_priority_domains = []
    if any(w in text for w in ["drop", "crack", "shatter", "broken"]):
        high_priority_domains.append("physical damage")
    if any(w in text for w in ["floating circle", "shortcut", "hover", "assistant menu"]):
        high_priority_domains.append("accessibility")
    if any(w in text for w in ["blue screen", "black screen with tiny text", "won't start up"]):
        high_priority_domains.append("bootloop")
    if any(w in text for w in ["plug in a charger", "charger", "charging"]):
        high_priority_domains.append("charging")
    if any(w in text for w in ["scrolling"]):
        high_priority_domains.append("scrolling")

    domains = high_priority_domains + domains
    if "after update" in text or "system update" in text:
        trigger_terms.append("post_system_update")
    elif "after app install" in text or "new app" in text:
        trigger_terms.append("post_app_install")

    prohibited_actions = []
    completed_actions = []

    if any(phrase in text for phrase in ["already tried", "i tried", "have tried", "restarted", "rebooted"]):
        if "restart" in text or "restarted" in text or "reboot" in text:
            completed_actions.append("restart")
        if "reset" in text or "factory reset" in text:
            completed_actions.append("reset")

    if any(phrase in text for phrase in ["do not", "don't", "without"]):
        if "reset" in text or "wipe" in text:
            prohibited_actions.append("reset")
        if "delete" in text:
            prohibited_actions.append("delete data")

    symptoms = []
    if any(w in text for w in ["drain", "draining", "drop", "dropping", "die", "dying", "dead", "overheat", "battery"]):
        symptoms.append("battery_drain")
    if any(w in text for w in ["connect", "connecting", "disconnect", "drop", "signal"]):
        if "wi-fi" in domains or "wifi" in text:
            symptoms.append("wifi_disconnection")
        if "bluetooth" in domains or "bt" in text:
            symptoms.append("bluetooth_pairing_failure")
    if any(w in text for w in ["location", "gps", "map", "accuracy"]):
        symptoms.append("location_inaccuracy")
    if any(w in text for w in ["flicker", "dark", "screen", "brightness", "blank", "white"]):
        symptoms.append("display_issue")
    if any(w in text for w in ["audio", "sound", "mute", "echo", "speaker"]):
        symptoms.append("audio_issue")
    if any(w in text for w in ["reset", "wipe", "no service"]):
        symptoms.append("network_reset_required")

    return FastCaseFeatures(
        normalized_query=text,
        probable_domains=list(dict.fromkeys(domains)),
        trigger_terms=trigger_terms,
        prohibited_actions=prohibited_actions,
        completed_actions=completed_actions,
        device_terms=device_terms if device_terms else ([norm_query.detected_device] if norm_query.detected_device else []),
        symptoms=symptoms
    )

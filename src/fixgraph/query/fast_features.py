from typing import List, Optional
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

    def to_symptom_atom(self) -> SymptomAtom:
        return SymptomAtom(
            device=self.device_terms[0] if self.device_terms else "Galaxy",
            domains=self.probable_domains,
            symptoms=[],
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
    
    if any(w in text for w in ["drain", "draining", "drop", "dropping", "die", "dying"]):
        domains.append("battery protection")
    if any(w in text for w in ["connect", "connecting", "disconnect", "drop", "signal"]):
        if "wi-fi" in domains or "wifi" in text:
            domains.append("wi-fi")
        if "bluetooth" in domains or "bt" in text:
            domains.append("bluetooth")
    if any(w in text for w in ["location", "gps", "map", "accuracy"]):
        domains.append("location")
    if any(w in text for w in ["flicker", "dark", "screen", "brightness"]):
        domains.append("display")
    if any(w in text for w in ["reset", "wipe", "no service"]):
        domains.append("reset mobile network settings")
        
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
            
    return FastCaseFeatures(
        normalized_query=text,
        probable_domains=sorted(set(domains)),
        trigger_terms=trigger_terms,
        prohibited_actions=prohibited_actions,
        completed_actions=completed_actions,
        device_terms=[norm_query.detected_device] if norm_query.detected_device else []
    )

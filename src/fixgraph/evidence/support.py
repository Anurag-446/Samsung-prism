"""Action evidence support checker to ensure semantic grounding."""

from typing import Dict

import numpy as np

from fixgraph.contracts.internal import CandidateAction, EvidenceSpan
from fixgraph.providers.embedder import get_embedder


class EvidenceSupportChecker:
    def __init__(self, threshold: float = 0.35):
        self.embedder = get_embedder()
        self.threshold = threshold

    def score_action_support(
        self, action: CandidateAction, evidence_map: Dict[str, EvidenceSpan]
    ) -> float:
        # Check if the referenced evidence IDs actually exist in the map
        if not evidence_map:
            return 0.0

        if not action.evidence_support and not action.evidence_ids:
            return 0.0

        # Extract supporting evidence referenced by the action
        ev_ids_to_check = set()
        if action.evidence_support:
            for es in action.evidence_support:
                ev_ids_to_check.add(es.evidence_id)
        if action.evidence_ids:
            for ev_id in action.evidence_ids:
                ev_ids_to_check.add(ev_id)

        valid_ev_spans = [
            evidence_map[ev_id] for ev_id in ev_ids_to_check if ev_id in evidence_map
        ]

        if not valid_ev_spans:
            return 0.0

        action_text = f"{action.intent} " + " ".join(action.steps)
        action_vec = np.array(self.embedder.encode_single(action_text), dtype=np.float32)

        # Detect contradictory evidence naively
        for ev in valid_ev_spans:
            text = ev.text_content.lower()
            if "do not" in text or "don't" in text or "avoid" in text:
                action_intent_lower = action.intent.lower()
                if any(w in text for w in action_intent_lower.split() if len(w) > 3):
                    # Conflict detected
                    return 0.0

        max_similarity = 0.0
        for ev in valid_ev_spans:
            ev_vec = np.array(self.embedder.encode_single(ev.text_content), dtype=np.float32)
            sim = float(np.dot(action_vec, ev_vec))
            if sim > max_similarity:
                max_similarity = sim

        if max_similarity < self.threshold:
            return 0.0

        return min(1.0, max_similarity)

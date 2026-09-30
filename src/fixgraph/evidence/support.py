"""Action evidence support checker to ensure semantic grounding."""

from typing import Dict

from fixgraph.contracts.internal import CandidateAction, EvidenceSpan


class EvidenceSupportChecker:
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

        # For phase 2 deterministic validation: we trust the LLM's support_score if it passes existence checks
        # But we ensure it meets the threshold
        max_score = 0.0
        if action.evidence_support:
            for es in action.evidence_support:
                if es.evidence_id in evidence_map:
                    max_score = max(max_score, es.support_score)
        else:
            # If it only provided IDs but no structured score, assume 0.9 as placeholder
            max_score = 0.9

        # Detect contradictory evidence very naively for now (e.g., if there's "do not" in one evidence span and "do" in another)
        # This will be hardened in later phases
        for ev in valid_ev_spans:
            text = ev.text_content.lower()
            if "do not" in text or "don't" in text or "avoid" in text:
                action_intent_lower = action.intent.lower()
                if any(w in text for w in action_intent_lower.split()):
                    # Conflict detected
                    return 0.0

        return max_score

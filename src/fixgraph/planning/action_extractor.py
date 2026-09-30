"""Action extractor for evidence-grounded candidate action generation (M3-06)."""
from typing import List, Tuple

from fixgraph.config import settings
from fixgraph.contracts.internal import CandidateAction, EvidenceSpan, SymptomAtom
from fixgraph.evidence.support import EvidenceSupportChecker
from fixgraph.providers.factory import create_llm_provider


class ActionExtractor:
    def __init__(self, llm_provider=None, support_checker=None):
        self.llm = llm_provider or create_llm_provider(settings)
        self.support_checker = support_checker or EvidenceSupportChecker()

    def extract_actions(
        self, query: str, atom: SymptomAtom, evidence_spans: List[EvidenceSpan]
    ) -> Tuple[List[CandidateAction], List[CandidateAction]]:

        result = self.llm.extract_candidate_actions(query, atom, evidence_spans)
        candidates = result.actions

        evidence_map = {e.evidence_id: e for e in evidence_spans}

        supported_actions = []
        unsupported_actions = []

        for c in candidates:
            score = self.support_checker.score_action_support(c, evidence_map)
            if score >= settings.min_action_evidence_score:
                supported_actions.append(c)
            else:
                unsupported_actions.append(c)

        return supported_actions, unsupported_actions

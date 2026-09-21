"""Action extractor for evidence-grounded candidate action generation (M3-06)."""

from typing import List
from fixgraph.contracts.internal import CandidateAction, EvidenceSpan, SymptomAtom
from fixgraph.providers.llm import MockLLMProvider


class ActionExtractor:
    def __init__(self, llm_provider: MockLLMProvider = None):
        self.llm = llm_provider or MockLLMProvider()

    def extract_actions(
        self, query: str, atom: SymptomAtom, evidence_spans: List[EvidenceSpan]
    ) -> List[CandidateAction]:
        candidates = self.llm.extract_candidate_actions(query, atom, evidence_spans)

        # Filter out ungrounded actions if evidence spans exist (P0-09)
        if evidence_spans:
            valid_ids = {e.evidence_id for e in evidence_spans}
            grounded: List[CandidateAction] = []
            for c in candidates:
                if any(ev in valid_ids for ev in c.evidence_ids):
                    grounded.append(c)
            return grounded or candidates

        return candidates

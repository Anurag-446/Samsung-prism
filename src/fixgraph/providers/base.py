from typing import List, Protocol

from fixgraph.contracts.internal import (
    CandidateActionExtractionResult,
    EvidenceSpan,
    SymptomAtom,
    SymptomExtractionResult,
)


class LLMProvider(Protocol):
    @property
    def provider_id(self) -> str: ...
    @property
    def model_id(self) -> str: ...

    def extract_symptoms(
        self, query: str, evidence: List[EvidenceSpan]
    ) -> SymptomExtractionResult: ...

    def extract_candidate_actions(
        self, query: str, symptoms: SymptomAtom, evidence: List[EvidenceSpan]
    ) -> CandidateActionExtractionResult: ...

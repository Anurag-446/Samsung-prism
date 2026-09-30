"""Local evidence retriever implementation."""
from typing import List

from fixgraph.contracts.internal import EvidenceSpan
from fixgraph.evidence.store import EvidenceStore


class LocalEvidenceRetriever(EvidenceStore):
    def retrieve(self, query: str, top_k: int = 8) -> List[EvidenceSpan]:
        # Minimal implementation for the challenge framework.
        # Uses available official/local data only.
        return []

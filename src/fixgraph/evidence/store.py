"""Reference evidence store abstraction."""
from typing import List, Protocol

from fixgraph.contracts.internal import EvidenceSpan


class EvidenceStore(Protocol):
    def retrieve(self, query: str, top_k: int = 8) -> List[EvidenceSpan]: ...

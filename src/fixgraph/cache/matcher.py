"""Two-stage semantic cache matcher with domain compatibility gates (M5-03 & M5-04)."""

from typing import List, Optional, Tuple
import numpy as np
from fixgraph.contracts.internal import CacheEntry, CaseSignature
from fixgraph.cache.store import CaseCacheStore
from fixgraph.providers.embedder import EmbedderProtocol, get_embedder


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class TwoStageCacheMatcher:
    def __init__(
        self,
        store: CaseCacheStore,
        embedder: EmbedderProtocol = None,
        similarity_threshold: float = 0.82,
    ):
        self.store = store
        self.embedder = embedder or get_embedder()
        self.similarity_threshold = similarity_threshold

    def lookup(
        self,
        signature: CaseSignature,
        query: str,
        catalog_fingerprint: str,
    ) -> Tuple[Optional[CacheEntry], float, str]:
        """Perform two-stage cache lookup returning (entry, similarity_score, match_reason)."""

        # Stage 1: Exact canonical case-signature lookup
        exact_entry = self.store.get_by_signature(signature.signature_hash)
        if exact_entry:
            # Fingerprint compatibility gate
            if exact_entry.catalog_fingerprint == catalog_fingerprint:
                return exact_entry, 1.0, "exact_signature_match"

        # Stage 2: Vector nearest-neighbor search over query embeddings
        query_vec = self.embedder.encode_single(query)
        all_entries = self.store.get_all_entries()

        best_entry: Optional[CacheEntry] = None
        best_sim = 0.0

        for entry in all_entries:
            # Fingerprint compatibility gate
            if entry.catalog_fingerprint != catalog_fingerprint:
                continue

            # Domain compatibility gate (P0-24 requirement)
            if signature.domain_primary not in entry.canonical_query:
                continue

            sim = _cosine_similarity(query_vec, entry.query_embedding)
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_entry and best_sim >= self.similarity_threshold:
            return best_entry, round(best_sim, 4), "semantic_vector_match"

        return None, round(best_sim, 4), "cache_miss"

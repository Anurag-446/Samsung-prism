"""Two-stage semantic cache matcher with domain compatibility gates (M5-03 & M5-04)."""

import json
from typing import List, Optional, Tuple

import numpy as np

from fixgraph.cache.invalidation import CacheCompatibilityValidator
from fixgraph.cache.store import CaseCacheStore
from fixgraph.config import settings
from fixgraph.contracts.internal import CacheEntry, CaseSignature, PipelineFingerprint
from fixgraph.observability.logging import logger
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
        similarity_threshold: float = None,
        min_margin: float = None
    ):
        self.store = store
        self.embedder = embedder or get_embedder()
        self.similarity_threshold = similarity_threshold if similarity_threshold is not None else settings.cache_semantic_threshold
        self.min_margin = min_margin if min_margin is not None else settings.cache_min_margin
        self.compatibility_validator = CacheCompatibilityValidator()

    def lookup(
        self,
        signature: CaseSignature,
        query: str,
        runtime_fingerprint: PipelineFingerprint,
    ) -> Tuple[Optional[CacheEntry], float, str]:
        """Perform two-stage cache lookup returning (entry, similarity_score, match_reason)."""

        # Stage 1: Exact canonical case-signature lookup
        exact_entry = self.store.get_by_signature(signature.signature_hash)
        if exact_entry:
            pipeline_compat = self.compatibility_validator.validate_pipeline(exact_entry, runtime_fingerprint)
            if pipeline_compat.compatible:
                return exact_entry, 1.0, "exact_signature_match"
            else:
                logger.debug(f"Exact signature matched but pipeline incompatible: {pipeline_compat.hard_failures}")

        # Stage 2: Vector nearest-neighbor search over query embeddings
        query_vec = self.embedder.encode_single(query)

        # Check current embedder properties
        current_dim = len(query_vec)

        all_entries = self.store.get_all_entries()

        candidates = []

        for entry in all_entries:
            # 1. Pipeline compatibility (embedder, catalog, schema, dimension)
            pipeline_compat = self.compatibility_validator.validate_pipeline(entry, runtime_fingerprint)
            if not pipeline_compat.compatible:
                continue

            # 2. Vector dimension check (should be caught by pipeline validation, but extra safety)
            if entry.embedding_dimension != current_dim or len(entry.query_embedding) != current_dim:
                continue

            # 3. Hard semantic compatibility gates
            try:
                cached_signature_dict = json.loads(entry.canonical_signature_json)
                cached_signature = CaseSignature.model_validate(cached_signature_dict)
            except Exception:
                continue # Skip corrupted entries

            semantic_compat = self.compatibility_validator.validate_semantics(cached_signature, signature)
            if not semantic_compat.compatible:
                continue

            sim = _cosine_similarity(query_vec, entry.query_embedding)
            candidates.append((sim, entry))

        if not candidates:
            return None, 0.0, "cache_miss_no_candidates"

        candidates.sort(key=lambda x: x[0], reverse=True)

        top1_sim, top1_entry = candidates[0]

        if top1_sim < self.similarity_threshold:
            return None, top1_sim, f"cache_miss_below_threshold_{top1_sim:.3f}"

        # Top-1 / Top-2 Margin evaluation
        if len(candidates) > 1:
            top2_sim, _ = candidates[1]
            margin = top1_sim - top2_sim
            if margin < self.min_margin:
                return None, top1_sim, f"cache_miss_ambiguous_margin_{margin:.3f}"

        return top1_entry, round(top1_sim, 4), "semantic_vector_match"

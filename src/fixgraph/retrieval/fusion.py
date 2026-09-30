"""Hybrid rank fusion combining sparse BM25 and dense vector scores (M2-04)."""

from typing import Dict, List

from fixgraph.contracts.internal import ScreenCandidate
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.retrieval.bm25_index import BM25Index
from fixgraph.retrieval.dense_index import DenseIndex


class HybridFusion:
    def __init__(
        self, catalog: DeeplinkCatalog, bm25_index: BM25Index = None, dense_index: DenseIndex = None
    ):
        self.catalog = catalog
        self.bm25 = bm25_index or BM25Index(catalog)
        self.dense = dense_index or DenseIndex(catalog)

    def search(self, query: str, top_k: int = 5, k_rrf: int = 60) -> List[ScreenCandidate]:
        """Perform Reciprocal Rank Fusion (RRF) over BM25 and Dense search results."""
        bm25_results = self.bm25.search(query, top_k=top_k * 2)
        dense_results = self.dense.search(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        bm25_score_map: Dict[str, float] = {}
        dense_score_map: Dict[str, float] = {}
        records_map: Dict[str, DeeplinkRecord] = {}

        # Process BM25 ranks
        for rank, (rec, score) in enumerate(bm25_results, start=1):
            rec_id = rec.record_id
            records_map[rec_id] = rec
            bm25_score_map[rec_id] = score
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + (1.0 / (k_rrf + rank))

        # Process Dense ranks
        for rank, (rec, score) in enumerate(dense_results, start=1):
            rec_id = rec.record_id
            records_map[rec_id] = rec
            dense_score_map[rec_id] = score
            rrf_scores[rec_id] = rrf_scores.get(rec_id, 0.0) + (1.0 / (k_rrf + rank))

        # Build candidate list and compute deterministic metadata score
        candidates: List[ScreenCandidate] = []
        max_bm25 = max(bm25_score_map.values()) if bm25_score_map else 1.0
        if max_bm25 == 0.0:
            max_bm25 = 1.0

        for rec_id, rec in records_map.items():
            bm_s = bm25_score_map.get(rec_id, 0.0)
            dn_s = dense_score_map.get(rec_id, 0.0)
            
            norm_bm25 = bm_s / max_bm25
            
            # Base combination
            base_score = (norm_bm25 * 0.4) + (dn_s * 0.6)
            
            # Metadata heuristics
            searchable_text = rec.get_searchable_text().lower()
            q_lower = query.lower()
            
            bonus = 0.0
            
            if rec.name.lower() in q_lower or q_lower in rec.name.lower():
                bonus += 0.15
            if rec.original_type and rec.original_type.lower() in q_lower:
                bonus += 0.05
            if rec.validation and rec.validation.get("key") and str(rec.validation.get("key")).lower() in q_lower:
                bonus += 0.05
                
            if "general" in rec.name.lower() or "misc" in rec.name.lower():
                bonus -= 0.1
                
            conf = min(max(base_score + bonus, 0.0), 1.0)

            candidates.append(
                ScreenCandidate(
                    catalog_record_id=rec_id,
                    exact_uri=rec.uri,
                    screen_name=rec.name,
                    bm25_score=float(bm_s),
                    dense_score=float(dn_s),
                    combined_score=float(conf),
                    confidence=conf,
                    matched_metadata=rec.get_searchable_text()[:100],
                )
            )

        candidates.sort(key=lambda x: x.combined_score, reverse=True)
        return candidates[:top_k]

"""Screen resolver mapping candidate actions to exact catalog records (M2-05)."""

from typing import Optional

from fixgraph.contracts.internal import ScreenCandidate
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.retrieval.fusion import HybridFusion


class ScreenResolver:
    def __init__(
        self, catalog: DeeplinkCatalog, fusion: HybridFusion = None
    ):
        from fixgraph.config import settings
        self.catalog = catalog
        self.fusion = fusion or HybridFusion(catalog)
        self.min_confidence = settings.screen_resolution_threshold
        self.min_margin = settings.screen_min_margin

    def resolve_action_intent(self, intent_text: str) -> Optional[ScreenCandidate]:
        """Resolve action intent to top exact catalog screen candidate or None if uncertain."""
        if not intent_text or not intent_text.strip():
            return None

        candidates = self.fusion.search(intent_text, top_k=3)
        if not candidates:
            return None

        top1 = candidates[0]
        # Rerank candidates based on specificity (originalType)
        # Deep links like Settings/Connections/Wi-Fi should win over Settings
        reranked = []
        for c in candidates:
            score = c.confidence
            record = self.catalog.get_by_id(c.catalog_record_id)
            if record and record.metadata and record.metadata.original_type:
                # Manager metadata: originalType = "App", "Menu", "Setting", "General"
                # Penalize generic types if query is specific
                o_type = record.metadata.original_type.lower()
                if o_type in ["general", "app"] and "settings" not in intent_text.lower():
                    score *= 0.8
            reranked.append((c, score))
            
        reranked.sort(key=lambda x: x[1], reverse=True)
        top1_tuple = reranked[0]
        top1_cand = top1_tuple[0]
        top1_score = top1_tuple[1]
        
        if top1_score < self.min_confidence:
            return None
            
        if len(reranked) > 1:
            top2_score = reranked[1][1]
            if (top1_score - top2_score) < self.min_margin:
                return None

        top1_cand.confidence = top1_score
        return top1_cand

    def get_catalog_record(self, record_id: str) -> Optional[DeeplinkRecord]:
        return self.catalog.get_by_id(record_id)

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
        if top1.confidence < self.min_confidence:
            return None
            
        if len(candidates) > 1:
            top2 = candidates[1]
            if (top1.confidence - top2.confidence) < self.min_margin:
                return None

        return top1

    def get_catalog_record(self, record_id: str) -> Optional[DeeplinkRecord]:
        return self.catalog.get_by_id(record_id)

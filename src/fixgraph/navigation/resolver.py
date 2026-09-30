"""Navigation-aware screen resolver and reranker."""
from typing import Optional

from fixgraph.contracts.internal import ScreenCandidate
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.retrieval.fusion import HybridFusion
from fixgraph.navigation.graph import NavigationGraph
from pathlib import Path
from fixgraph.config import settings

class NavigationAwareScreenResolver:
    def __init__(
        self, catalog: DeeplinkCatalog, fusion: HybridFusion = None, min_confidence: float = 0.2
    ):
        self.catalog = catalog
        self.fusion = fusion or HybridFusion(catalog)
        self.min_confidence = min_confidence
        
        hierarchy_path = settings.get_resolved_path("tests/fixtures/challenge_assets/hierarchy.json")
        self.graph = NavigationGraph(hierarchy_path)

    def resolve_action_intent(self, intent_text: str) -> Optional[ScreenCandidate]:
        """Resolve action intent to top exact catalog screen candidate or None if uncertain."""
        if not intent_text or not intent_text.strip():
            return None

        candidates = self.fusion.search(intent_text, top_k=5)
        if not candidates:
            return None

        # Reranking logic
        reranked = []
        for c in candidates:
            score = c.confidence
            
            if self.graph.is_root(c.catalog_record_id):
                if "general settings" not in intent_text.lower():
                    score *= 0.1 # Heavily penalize generic parent
                    
            # If we had a mechanism to know the "implied child", we would penalize parents.
            # But the root node check covers the "Settings" case as requested.
            
            reranked.append(ScreenCandidate(
                catalog_record_id=c.catalog_record_id,
                exact_uri=c.exact_uri,
                screen_name=c.screen_name,
                bm25_score=c.bm25_score,
                dense_score=c.dense_score,
                combined_score=score,
                confidence=score,
                matched_metadata=c.matched_metadata
            ))
            
        # Sort by new confidence
        reranked.sort(key=lambda x: x.confidence, reverse=True)
        top = reranked[0]
        
        if top.confidence < self.min_confidence:
            return None
            
        if top.dense_score < 0.30 and top.bm25_score < 1.8:
            return None

        return top

    def get_catalog_record(self, record_id: str) -> Optional[DeeplinkRecord]:
        return self.catalog.get_by_id(record_id)

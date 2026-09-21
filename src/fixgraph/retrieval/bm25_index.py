"""BM25 search index over descriptive catalog metadata (P1-11)."""

import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord


def tokenize_text(text: str) -> List[str]:
    """Tokenize Settings phrases into lowercase alphanumeric terms."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1]


class BM25Index:
    def __init__(self, catalog: DeeplinkCatalog):
        self.catalog = catalog
        self.records: List[DeeplinkRecord] = list(catalog.iter_records())
        self.corpus_tokens: List[List[str]] = [
            tokenize_text(r.get_searchable_text()) for r in self.records
        ]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DeeplinkRecord, float]]:
        """Search top_k catalog records using BM25 scoring over descriptive metadata."""
        if not self.bm25 or not self.records:
            return []

        tokens = tokenize_text(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        scored_pairs = list(zip(self.records, scores))
        # Sort descending by score
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

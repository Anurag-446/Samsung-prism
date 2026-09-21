"""Dense vector index over descriptive catalog metadata (P1-12)."""

from typing import List, Tuple
import numpy as np
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.providers.embedder import EmbedderProtocol, get_embedder


class DenseIndex:
    def __init__(self, catalog: DeeplinkCatalog, embedder: EmbedderProtocol = None):
        self.catalog = catalog
        self.records: List[DeeplinkRecord] = list(catalog.iter_records())
        self.embedder = embedder or get_embedder()

        # Pre-encode all catalog records
        texts = [r.get_searchable_text() for r in self.records]
        if texts:
            embeddings_list = self.embedder.encode_batch(texts)
            self.vectors = np.array(embeddings_list, dtype=np.float32)
        else:
            self.vectors = np.empty((0, 256), dtype=np.float32)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DeeplinkRecord, float]]:
        """Search top_k catalog records using cosine similarity over dense embeddings."""
        if len(self.records) == 0 or len(self.vectors) == 0:
            return []

        q_vec = np.array(self.embedder.encode_single(query), dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Compute cosine similarity dot products
        scores = np.dot(self.vectors, q_vec)

        scored_pairs = list(zip(self.records, [float(s) for s in scores]))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

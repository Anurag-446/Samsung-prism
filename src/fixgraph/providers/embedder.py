"""Embedding provider interface with lightweight CPU fallback and sentence-transformers support."""

import re
from typing import List, Protocol

import numpy as np

from fixgraph.config import settings
from fixgraph.providers.exceptions import EmbedderInitializationError


class EmbedderProtocol(Protocol):
    @property
    def model_fingerprint(self) -> str: ...

    def encode_single(self, text: str) -> List[float]: ...

    def encode_batch(self, texts: List[str]) -> List[List[float]]: ...


class HashNGramEmbedder:
    """Lightweight deterministic TF-IDF / character-gram vector embedder for portable CPU environments."""

    def __init__(self, vocab_size: int = 256):
        self.vocab_size = vocab_size
        self._fingerprint = "hashngram-v1"

    @property
    def model_fingerprint(self) -> str:
        return self._fingerprint

    def _text_to_vector(self, text: str) -> np.ndarray:
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        words = clean.split()
        vec = np.zeros(self.vocab_size, dtype=np.float32)

        for w in words:
            idx = sum(ord(c) for c in w) % self.vocab_size
            vec[idx] += 1.0

            # Character bi-grams
            for i in range(len(w) - 1):
                bg_idx = (ord(w[i]) * 31 + ord(w[i + 1])) % self.vocab_size
                vec[bg_idx] += 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def encode_single(self, text: str) -> List[float]:
        return self._text_to_vector(text).tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.encode_single(t) for t in texts]


def get_embedder() -> EmbedderProtocol:
    """Return configured embedder instance."""
    if settings.embedder_provider == "hashngram":
        return HashNGramEmbedder()

    try:
        from sentence_transformers import SentenceTransformer

        class SentenceTransformerWrapper:
            def __init__(self, model_name: str = settings.embedding_model_name):
                self.model_name = model_name
                self.model = SentenceTransformer(model_name)

            @property
            def model_fingerprint(self) -> str:
                return f"st-{self.model_name}"

            def encode_single(self, text: str) -> List[float]:
                emb = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return emb.tolist()

            def encode_batch(self, texts: List[str]) -> List[List[float]]:
                embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embs.tolist()

        return SentenceTransformerWrapper()
    except Exception as e:
        if settings.allow_embedder_fallback:
            return HashNGramEmbedder()
        raise EmbedderInitializationError(f"Failed to load sentence-transformers model {settings.embedding_model_name}: {e}")

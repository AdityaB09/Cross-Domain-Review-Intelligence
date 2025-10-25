# backend/services/semantic_index.py

import json
import os
from typing import List, Dict, Any

import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from core.config import settings


# --- Embedder singleton -------------------------------------------------
#
# We load the same model you declared in core/config.py:
#   settings.emb_model = "sentence-transformers/all-MiniLM-L6-v2"
#
# This model outputs 384-dim sentence embeddings. We normalize them so
# cosine similarity ~= dot product in FAISS.
#
# We keep it global so it loads once per process.
#
_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.emb_model)
    return _embedder


def get_query_embedding(text: str) -> np.ndarray:
    """
    Encode query text into the same embedding space as the FAISS index.

    Returns shape (1, dim) float32.
    """
    model = _get_embedder()
    vec = model.encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,  # so similarity is cosine-like
    )
    # FAISS wants float32
    return vec.astype("float32")


# --- SemanticIndex ------------------------------------------------------


class SemanticIndex:
    """
    Wrapper around FAISS + metadata.

    Assumes:
    - settings.faiss_index_path -> /data/index/index.faiss
    - settings.faiss_meta_path  -> /data/index/meta.json

    meta.json should be a list where meta[i] corresponds to the same row
    used when building index.faiss.
    """

    def __init__(self) -> None:
        self.index = None
        self.meta: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        meta_path = str(settings.faiss_meta_path)
        faiss_path = str(settings.faiss_index_path)

        # load review metadata
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
        else:
            self.meta = []

        # load FAISS index
        if os.path.exists(faiss_path):
            self.index = faiss.read_index(faiss_path)
        else:
            self.index = None

    def is_ready(self) -> bool:
        return self.index is not None and len(self.meta) > 0

    def search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """
        Return top-k nearest rows with a 'score' field.

        score is FAISS distance. Lower distance == closer for L2 indexes.
        If you built with cosine/inner-product, higher is better.
        We just surface it raw so the UI can show "Relevance".
        """
        if not self.is_ready():
            raise RuntimeError("Index not built yet or empty.")

        emb = get_query_embedding(query)  # (1, dim)

        distances, indices = self.index.search(emb, k)
        distances = distances[0]
        indices = indices[0]

        results: List[Dict[str, Any]] = []
        for dist, idx in zip(distances, indices):
            if idx < 0 or idx >= len(self.meta):
                continue

            row = dict(self.meta[idx])
            row["score"] = float(dist)
            results.append(row)

        return results

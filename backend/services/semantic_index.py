# services/semantic_index.py

from typing import List, Dict, Any
from pathlib import Path
import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from core.config import settings  # we already saw settings in your config


class SemanticIndex:
    """
    Thin wrapper around FAISS index + metadata so the API can just call search().
    Assumptions:
      - settings.index_dir points to a directory persisted with docker volume (/data/index)
      - faiss_index_path : index.faiss
      - faiss_meta_path  : meta.json (list[{"text": "...", ...}, ...] aligned to FAISS ids)
    """

    def __init__(self):
        self.index_dir: Path = settings.index_dir
        self.index_path: Path = settings.faiss_index_path
        self.meta_path: Path = settings.faiss_meta_path

        # embed model name is in settings.emb_model
        self.model = SentenceTransformer(settings.emb_model)

        # load FAISS
        if not self.index_path.exists():
            raise RuntimeError(
                f"FAISS index not found at {self.index_path}. "
                "You need to ingest/build first."
            )

        if not self.meta_path.exists():
            raise RuntimeError(
                f"Metadata file not found at {self.meta_path}. "
                "Cannot map neighbors back to text."
            )

        # load metadata rows
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta: List[Dict[str, Any]] = json.load(f)
            # meta[i]["text"] should be the review text string

        # load the faiss index
        self.index = faiss.read_index(str(self.index_path))

        # basic safety: make sure dim matches model
        dim = self.index.d
        test_vec = self.model.encode(["dimension check"], convert_to_numpy=True)
        if test_vec.shape[1] != dim:
            raise RuntimeError(
                f"FAISS dim {dim} != model dim {test_vec.shape[1]}. "
                "Index was probably built with a different model."
            )

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Returns a list of { "text": <review text>, "score": <similarity> }
        score = cosine similarity 0..1-ish
        """

        if not query or not query.strip():
            return []

        # embed query -> L2 normalize for cosine sim
        q_emb = self.model.encode([query], convert_to_numpy=True)  # shape (1, dim)
        q_norm = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)

        # the FAISS index may be IVF/Flat/etc. We'll just search k=top_k
        # raw distance from faiss is usually inner product or L2 depending on build.
        # we assume index was built with IndexFlatIP on normalized vectors.
        D, I = self.index.search(q_norm.astype(np.float32), top_k)

        # D: (1, top_k) similarity scores, I: (1, top_k) indices into meta
        hits: List[Dict[str, Any]] = []
        for rank, (idx, score) in enumerate(zip(I[0], D[0])):
            if idx < 0 or idx >= len(self.meta):
                continue
            text = self.meta[idx].get("text", "")
            hits.append(
                {
                    "text": text,
                    "score": float(score),
                }
            )

        return hits

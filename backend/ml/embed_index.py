import os
import json
from typing import List, Dict, Any

import numpy as np
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text

# ---- config ----
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://cdri:cdri@postgres:5432/cdri",
)
INDEX_DIR = os.getenv("INDEX_DIR", "/data/index")
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class EmbIndex:
    """
    - pull reviews from Postgres
    - embed them with sentence-transformers
    - build FAISS IP index
    - serve semantic search
    """

    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.model = SentenceTransformer(EMB_MODEL)

        os.makedirs(INDEX_DIR, exist_ok=True)
        self.faiss_path = os.path.join(INDEX_DIR, "index.faiss")
        self.meta_path = os.path.join(INDEX_DIR, "meta.json")

        self.index = None  # faiss.IndexFlatIP
        self.meta: List[Dict[str, Any]] = []

    def build(self) -> None:
        """
        Build index from whatever is in the `reviews` table.
        Writes both FAISS index + metadata file to disk.
        """

        # 1. fetch rows from DB
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, text FROM reviews"))
            # SQLAlchemy 2.x returns Row objects; use ._mapping
            rows = [dict(r._mapping) for r in result]

        # no data case
        if not rows:
            self._save_empty()
            return

        ids = [row["id"] for row in rows]
        texts = [row["text"] for row in rows]

        # 2. embed -> normalized float32
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)

        # 3. build FAISS index (cosine == dot product because normalized)
        dim = embeddings.shape[1]
        faiss_index = faiss.IndexFlatIP(dim)
        faiss_index.add(embeddings)

        # 4. save index + metadata
        faiss.write_index(faiss_index, self.faiss_path)

        meta_list = []
        for rid, txt in zip(ids, texts):
            meta_list.append(
                {
                    "id": rid,
                    "text": txt,
                }
            )

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_list, f)

        # keep in memory
        self.index = faiss_index
        self.meta = meta_list

    def _save_empty(self) -> None:
        """
        If there are zero rows, create an empty index so healthcheck doesn't stay degraded.
        """
        dim = 384  # all-MiniLM-L6-v2 output size
        faiss_index = faiss.IndexFlatIP(dim)

        faiss.write_index(faiss_index, self.faiss_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump([], f)

        self.index = faiss_index
        self.meta = []

    def _load_from_disk(self) -> None:
        """
        Lazy-load FAISS + metadata into memory.
        """
        if not (os.path.exists(self.faiss_path) and os.path.exists(self.meta_path)):
            self.index = None
            self.meta = []
            return

        faiss_index = faiss.read_index(self.faiss_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta_list = json.load(f)

        self.index = faiss_index
        self.meta = meta_list

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Return top-k matches from FAISS.
        Each hit: {rank, id, text, score}
        """

        # make sure index + meta are in memory
        if self.index is None or not self.meta:
            self._load_from_disk()

        if self.index is None or not self.meta:
            # still nothing indexed
            return []

        q_emb = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        if q_emb.dtype != np.float32:
            q_emb = q_emb.astype(np.float32)

        scores, idxs = self.index.search(q_emb, k)
        idxs = idxs[0]
        scores = scores[0]

        out: List[Dict[str, Any]] = []
        for rank, (i, sc) in enumerate(zip(idxs, scores)):
            if i < 0 or i >= len(self.meta):
                continue
            m = self.meta[i]
            out.append(
                {
                    "rank": rank,
                    "id": m["id"],
                    "text": m["text"],
                    "score": float(sc),
                }
            )
        return out


# global singleton, this is what the routes import
index = EmbIndex()

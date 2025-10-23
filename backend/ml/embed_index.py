from sentence_transformers import SentenceTransformer
import faiss, numpy as np, os, json
from sqlalchemy import text
from core.db import engine
from core.config import settings

INDEX_DIR = os.path.join(settings.data_dir, "faiss")
os.makedirs(INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(INDEX_DIR, "index_ip.bin")
IDS_PATH = os.path.join(INDEX_DIR, "ids.npy")

class EmbIndex:
    def __init__(self, model="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model)
        self.index = None
        self.ids = []

    def build(self):
        with engine.begin() as conn:
            rows = [dict(x) for x in conn.execute(text("SELECT id,text FROM reviews"))]
        if not rows:
            self.index = faiss.IndexFlatIP(384)
            self.ids = []
            return
        embs = self.model.encode([r["text"] for r in rows], convert_to_numpy=True, show_progress_bar=True)
        d = embs.shape[1]
        faiss.normalize_L2(embs)
        self.index = faiss.IndexFlatIP(d)
        self.index.add(embs)
        self.ids = [r["id"] for r in rows]
        faiss.write_index(self.index, INDEX_PATH)
        np.save(IDS_PATH, np.array(self.ids))

    def _ensure_loaded(self):
        if self.index is None and os.path.exists(INDEX_PATH) and os.path.exists(IDS_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            self.ids = np.load(IDS_PATH).tolist()

    def query(self, q, k=10):
        self._ensure_loaded()
        if self.index is None or len(self.ids) == 0:
            return []
        v = self.model.encode([q], convert_to_numpy=True)
        faiss.normalize_L2(v)
        D,I = self.index.search(v, k)
        out = []
        with engine.begin() as conn:
            for idx in I[0]:
                if idx < 0 or idx >= len(self.ids): continue
                rid = self.ids[idx]
                row = conn.execute(text(
                    "SELECT id,domain,product,text FROM reviews WHERE id=:i"),
                    {"i": rid}
                ).fetchone()
                if row: out.append(dict(row))
        return out

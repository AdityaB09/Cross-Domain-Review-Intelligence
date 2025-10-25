# backend/services/index_bootstrap.py
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from core.config import settings
from core.logging import get_logger
from services.public_data import PublicDataLoader

log = get_logger("index_bootstrap")

def _ensure_dirs():
    settings.index_dir.mkdir(parents=True, exist_ok=True)

def _canonical_text(row: Dict[str, Any]) -> str:
    """
    Build the text we embed for retrieval.
    We include product/domain/source to help recall.
    """
    product = row.get("product") or ""
    cond    = row.get("condition") or ""
    txt     = row.get("text") or ""
    src     = row.get("source", "?")
    dom     = row.get("domain", "?")
    return f"[{src} {dom}] {product} {cond} :: {txt}"

def build_index(max_items_per_source: int = 1000, batch_size: int = 256) -> Tuple[int, int]:
    """
    Cold-start / demo index builder.

    Streams public data (not from Postgres), embeds with SentenceTransformer,
    normalizes, and writes:
      - settings.faiss_index_path  (index.faiss)
      - settings.faiss_meta_path   (meta.json lines)
    Returns (total_seen, kept_indexed).
    """
    _ensure_dirs()

    loader = PublicDataLoader(max_items=max_items_per_source)
    model = SentenceTransformer(settings.emb_model)
    dim = model.get_sentence_embedding_dimension()

    # cosine sim via inner product on L2-normalized vectors
    index = faiss.IndexFlatIP(dim)

    total = 0
    kept = 0
    buf_vecs: List[np.ndarray] = []
    buf_meta: List[Dict[str, Any]] = []

    meta_tmp_path = settings.faiss_meta_path
    # overwrite old meta
    if meta_tmp_path.exists():
        meta_tmp_path.unlink()

    def flush():
        nonlocal buf_vecs, buf_meta, index
        if not buf_vecs:
            return
        mat = np.vstack(buf_vecs).astype("float32")
        faiss.normalize_L2(mat)
        index.add(mat)
        with open(meta_tmp_path, "a", encoding="utf-8") as f:
            for m in buf_meta:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        buf_vecs.clear()
        buf_meta.clear()

    for row in loader.stream_all():
        total += 1
        text = _canonical_text(row).strip()
        if not text:
            continue

        vec = model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=False,
        )

        buf_vecs.append(vec)
        buf_meta.append({
            "id": row.get("id"),
            "product": row.get("product"),
            "domain": row.get("domain"),
            "source": row.get("source"),
            "text": row.get("text"),
            "rating": row.get("rating"),
            "date": row.get("date"),
        })
        kept += 1

        if len(buf_vecs) >= batch_size:
            flush()

    flush()

    # write FAISS index file
    faiss.write_index(index, str(settings.faiss_index_path))

    log.info(
        "Bootstrap index built total_seen={} kept={} index_path={} meta_path={}",
        total,
        kept,
        settings.faiss_index_path,
        settings.faiss_meta_path,
    )

    return total, kept

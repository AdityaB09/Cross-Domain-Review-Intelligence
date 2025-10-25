# backend/services/remote_stream.py
import gzip
import io
import json
import csv
import urllib.request
import os
from typing import Iterator, Dict, Optional
from core.logging import get_logger

log = get_logger("remote_stream")

def _open_local(path: str):
    # returns a binary file-like
    return open(path, "rb")

def _http_open(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except Exception as e:
        log.error("Failed to fetch {}: {}", url, e)
        raise
    return resp  # file-like

def _smart_open(url_or_path: str):
    """
    If it's an http/https URL, fetch remotely.
    Otherwise, treat it as a local file path and open it.
    """
    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        return _http_open(url_or_path)
    # local path case
    if not os.path.exists(url_or_path):
        raise FileNotFoundError(f"Local path not found: {url_or_path}")
    return _open_local(url_or_path)

def stream_jsonl_gz(url_or_path: str, domain: str, max_items: Optional[int] = None):
    with _smart_open(url_or_path) as raw:
        gz = gzip.GzipFile(fileobj=io.BufferedReader(raw))
        count = 0
        for line in gz:
            if not line:
                break
            try:
                obj = json.loads(line.decode("utf-8", errors="ignore"))
            except Exception as e:
                log.warning("Bad JSONL_GZ line skipped: {}", e)
                continue
            yield _normalize_row(obj, domain)
            count += 1
            if max_items and count >= max_items:
                break

def stream_jsonl(url_or_path: str, domain: str, max_items: Optional[int] = None):
    with _smart_open(url_or_path) as raw:
        count = 0
        for raw_line in raw:
            try:
                obj = json.loads(raw_line.decode("utf-8", errors="ignore"))
            except Exception as e:
                log.warning("Bad JSONL line skipped: {}", e)
                continue
            yield _normalize_row(obj, domain)
            count += 1
            if max_items and count >= max_items:
                break

def stream_delim(url_or_path: str, domain: str, delimiter: str, max_items: Optional[int] = None):
    with _smart_open(url_or_path) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="ignore"), delimiter=delimiter)
        count = 0
        for row in reader:
            try:
                yield _normalize_row(row, domain)
            except Exception as e:
                log.warning("Bad CSV/TSV row skipped: {}", e)
                continue
            count += 1
            if max_items and count >= max_items:
                break

def _normalize_row(obj: Dict, domain: str) -> Dict:
    """
    Normalize arbitrary review row into our internal shape.
    We handle Amazon-style keys:
      - reviewText  -> text
      - overall     -> rating
      - asin        -> product
      - reviewerID  -> id
    Fallbacks for other sources too.
    """
    text   = (
        obj.get("reviewText")
        or obj.get("review")
        or obj.get("text")
        or obj.get("content")
        or ""
    )
    rating = obj.get("overall") or obj.get("rating") or None
    date   = obj.get("reviewTime") or obj.get("date") or obj.get("review_date") or obj.get("created")
    prod   = obj.get("asin") or obj.get("product") or obj.get("product_id") or obj.get("drugName") or obj.get("title")
    rid    = obj.get("reviewerID") or obj.get("review_id") or obj.get("uniqueID") or obj.get("id")

    return {
        "id": str(rid) if rid is not None else None,
        "text": str(text),
        "rating": float(rating) if rating not in (None, "", "NaN") else None,
        "date": str(date) if date else None,
        "product": str(prod) if prod else None,
        "domain": domain,
        "raw": obj,
    }

def stream_remote(kind: str, url_or_path: str, domain: str, max_items: Optional[int] = None):
    kind = kind.lower()
    if kind == "jsonl_gz":
        return stream_jsonl_gz(url_or_path, domain, max_items)
    if kind == "jsonl":
        return stream_jsonl(url_or_path, domain, max_items)
    if kind == "csv":
        return stream_delim(url_or_path, domain, ",", max_items)
    if kind == "tsv":
        return stream_delim(url_or_path, domain, "\t", max_items)
    raise ValueError(f"Unsupported remote kind: {kind}")

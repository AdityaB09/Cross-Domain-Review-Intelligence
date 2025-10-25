# backend/services/public_data.py
from typing import Iterator, Dict, Any, List
from core.config import settings, RemoteSource
from services.remote_stream import stream_remote

class PublicDataLoader:
    """
    Streams review-like rows from all configured bootstrap sources
    (settings.bootstrap_sources). This is used for cold-start indexing
    without touching Postgres.
    """

    def __init__(self, sources: List[RemoteSource] | None = None, max_items: int = 1000):
        # allow override for testing, else pull from settings
        self.sources = sources if sources is not None else settings.bootstrap_sources
        self.max_items = max_items

    def stream_all(self) -> Iterator[Dict[str, Any]]:
        """
        Yields dicts shaped like:
        {
          "id": ...,
          "text": ...,
          "rating": ...,
          "date": ...,
          "product": ...,
          "domain": ...,
          "source": <source.name>,
        }
        """
        for src in self.sources:
            # src is RemoteSource(dataclass)
            # we call stream_remote() with the right fmt/url/domain
            for row in stream_remote(
                kind=src.fmt,
                url=src.url,
                domain=src.domain or src.name,
                max_items=self.max_items,
            ):
                if not row.get("text"):
                    continue
                # enrich with "source" field for later debugging
                row["source"] = src.name
                yield row

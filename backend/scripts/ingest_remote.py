#!/usr/bin/env python3
import argparse
from sqlalchemy import text
from core.db import SessionLocal, init_db
from services.remote_stream import stream_remote

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--url",
        required=True,
        help="Remote data source URL (jsonl, jsonl.gz, csv, tsv)"
    )
    ap.add_argument(
        "--kind",
        required=True,
        choices=["jsonl","jsonl_gz","csv","tsv"],
        help="Format of the remote data"
    )
    ap.add_argument(
        "--domain",
        required=True,
        help="Domain label to store (e.g. 'amazon', 'drugs', 'reddit')"
    )
    ap.add_argument(
        "--max-items",
        type=int,
        default=1000,
        help="How many rows to sample from the remote source"
    )
    args = ap.parse_args()

    # make sure tables exist
    init_db()

    sess = SessionLocal()
    inserted = 0
    try:
        for row in stream_remote(
            args.kind,
            args.url,
            args.domain,
            max_items=args.max_items
        ):
            # remote_stream.py normalizes the row into:
            # {
            #   "id": ...,
            #   "text": ...,
            #   "rating": ...,
            #   "date": ...,
            #   "product": ...,
            #   "domain": args.domain,
            #   "raw": {...}
            # }
            txt = row.get("text") or ""
            if not txt.strip():
                continue

            sess.execute(
                text("""
                    INSERT INTO reviews (domain, product, text, rating)
                    VALUES (:domain, :product, :text, :rating)
                """),
                {
                    "domain": row.get("domain") or args.domain,
                    "product": row.get("product") or "unknown",
                    "text": txt,
                    "rating": row.get("rating"),
                },
            )
            inserted += 1

        sess.commit()
        print(f"[ingest_remote] inserted {inserted} rows from {args.url}")

    finally:
        sess.close()

if __name__ == "__main__":
    main()

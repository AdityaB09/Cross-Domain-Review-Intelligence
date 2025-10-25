#!/usr/bin/env python3
import argparse, json, gzip, os, sys
from pathlib import Path

try:
    import pandas as pd
except Exception as e:
    print("pandas is required inside the backend image", e, file=sys.stderr); raise

def write_jsonl(rows, out_path, limit):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows):
            if limit and i >= limit: break
            f.write(json.dumps(r, ensure_ascii=False)+"\n")

def load_drugscom(parquet_path, n):
    df = pd.read_parquet(parquet_path)
    # expected columns vary across mirrors; map safely
    text = df.get("review") or df.get("content") or df.get("text")
    drug = df.get("drugName") or df.get("drug") or df.get("medication")
    cond = df.get("condition") or df.get("disease") or df.get("domain")
    rating = df.get("rating") or df.get("score")
    date = df.get("date") or df.get("created") or df.get("timestamp")
    out = []
    for i in range(len(df)):
        out.append({
            "id": f"drugscom-{i}",
            "domain": "health",
            "product": (drug.iloc[i] if drug is not None else None) or "unknown",
            "condition": (cond.iloc[i] if cond is not None else None),
            "text": (text.iloc[i] if text is not None else ""),
            "rating": float(rating.iloc[i]) if rating is not None and pd.notna(rating.iloc[i]) else None,
            "date": str(date.iloc[i]) if date is not None else None,
            "source": "drugscom"
        })
    return out[:n] if n else out

def load_amazon(json_or_gz, n):
    def stream():
        opener = gzip.open if str(json_or_gz).endswith(".gz") else open
        with opener(json_or_gz, "rt", encoding="utf-8") as f:
            for i, line in enumerate(f):
                try:
                    j = json.loads(line)
                except Exception:
                    continue
                yield {
                    "id": f"amazon-{i}",
                    "domain": "general",
                    "product": j.get("asin") or j.get("product_id") or "unknown",
                    "text": j.get("reviewText") or j.get("review_text") or j.get("summary") or "",
                    "rating": j.get("overall") or j.get("rating"),
                    "date": j.get("reviewTime") or j.get("unixReviewTime"),
                    "source": "amazon"
                }
    rows=[]
    for i, r in enumerate(stream()):
        if n and i>=n: break
        rows.append(r)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drugscom-in", required=True, help="Parquet file from Drugs.com HF mirror")
    ap.add_argument("--amazon-in", required=True, help="Amazon reviews JSON or JSON.GZ")
    ap.add_argument("--out-dir", default="data/prepared")
    ap.add_argument("--n", type=int, default=1000)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    print("Loading Drugs.com…")
    drows = load_drugscom(args.drugscom_in, args.n)
    print(f"Loaded {len(drows)}")

    print("Loading Amazon…")
    arows = load_amazon(args.amazon_in, args.n)
    print(f"Loaded {len(arows)}")

    write_jsonl(drows, out_dir / "drugscom_min.jsonl", args.n)
    write_jsonl(arows, out_dir / "amazon_electronics_min.jsonl", args.n)
    print("Wrote:", out_dir / "drugscom_min.jsonl", "and", out_dir / "amazon_electronics_min.jsonl")

if __name__ == "__main__":
    main()

import gzip
import json
import requests
import time

BACKEND = "https://cdri-backend.onrender.com"  # <-- set this
PATH = "data/reviews_Electronics_5.json.gz"      # <-- local path
BATCH_SIZE = 200
MAX_TOTAL = 1000  # stop after this many reviews, so we don't spam

def yield_reviews(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # the lines you showed are JSON with keys like reviewerID, reviewText, overall, ...
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # fallback - treat whole line as text
                yield line
                continue

            text = obj.get("reviewText", "") or obj.get("summary", "")
            if text:
                yield text.strip()

def chunked(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

def main():
    total_sent = 0
    for batch in chunked(yield_reviews(PATH), BATCH_SIZE):
        # don't exceed MAX_TOTAL
        if total_sent >= MAX_TOTAL:
            break
        remaining = MAX_TOTAL - total_sent
        if len(batch) > remaining:
            batch = batch[:remaining]

        payload = {"lines": batch}
        resp = requests.post(f"{BACKEND}/ingest/jsonl", json=payload, timeout=30)
        if resp.status_code != 200:
            print("Backend error:", resp.status_code, resp.text)
            break
        data = resp.json()
        total_sent += data.get("ingested", 0)
        print(f"Ingested so far: {total_sent}")
        time.sleep(1.0)

    print("Done. Total ingested:", total_sent)

if __name__ == "__main__":
    main()

import sys, pickle
from pathlib import Path

import numpy as np
import pandas as pd
import faiss
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import client
from src.text_utils import normalize, tokenize

MODEL = "openai/text-embedding-3-small"


def build_index(n=5000, seed=42):
    idx_dir = ROOT / "data" / "indices"
    proc_dir = ROOT / "data" / "processed"
    idx_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)

    # 1. Prepare comments
    comments = pd.read_parquet(ROOT / "data/raw/comments_v0.parquet")
    comments["text"] = (
        comments["title"].fillna("") + " " + comments["body"].fillna("")
    ).map(normalize)
    comments = comments[comments["text"].str.len() >= 5].drop_duplicates("text")
    df = comments.sample(min(n, len(comments)), random_state=seed).reset_index(
        drop=True
    )

    # 2. Join product info (display/filter only, not indexed)
    prod = pd.read_parquet(
        ROOT / "data/raw/products_v0.parquet",
        columns=["id", "title_fa", "Brand", "Category1"],
    ).rename(
        columns={
            "id": "product_id",
            "title_fa": "product_title",
            "Brand": "brand",
            "Category1": "category",
        }
    )
    assert prod["product_id"].is_unique, "Duplicate product_id in products"

    df = df.merge(prod, on="product_id", how="left")
    print(
        f"comments: {len(df)} | missing product info: {df['product_title'].isna().mean():.1%}"
    )
    df[["product_title", "brand", "category"]] = df[
        ["product_title", "brand", "category"]
    ].fillna("")

    keep = ["id", "product_id", "product_title", "brand", "category", "text"]
    df[keep].to_parquet(proc_dir / "index_comments.parquet")

    # 3. BM25
    bm25 = BM25Okapi([tokenize(t) for t in df["text"]])
    with open(idx_dir / "bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)

    # 4. Embeddings (cache used only if row count matches)
    cache = idx_dir / "emb.npy"
    if cache.exists() and np.load(cache, mmap_mode="r").shape[0] == len(df):
        emb = np.load(cache)
        print("Loaded embeddings from cache")
    else:
        vecs = []
        texts = df["text"].str.slice(0, 2000).tolist()
        for i in range(0, len(texts), 100):
            response = client.embeddings.create(model=MODEL, input=texts[i : i + 100])
            vecs += [item.embedding for item in response.data]
            print(i, end=" ", flush=True)
        emb = np.array(vecs, dtype="float32")
        np.save(cache, emb)

    # 5. FAISS
    faiss.normalize_L2(emb)
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)
    faiss.write_index(index, str(idx_dir / "faiss.index"))
    print("\ndone", emb.shape)


if __name__ == "__main__":
    build_index()

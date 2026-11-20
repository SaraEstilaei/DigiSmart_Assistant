import pickle
from pathlib import Path

import faiss
import numpy as np
import pandas as pd

from src.config import client
from src.text_utils import normalize, tokenize

ROOT = Path(__file__).resolve().parents[1]
IDX_DIR = ROOT / "data" / "indices"
PROC_DIR = ROOT / "data" / "processed"
MODEL = "openai/text-embedding-3-small"

_state = None


def _load():
    """Load BM25, FAISS and comment table once. Run build_index() before this."""
    global _state
    if _state is None:
        with open(IDX_DIR / "bm25.pkl", "rb") as f:
            bm25 = pickle.load(f)
        index = faiss.read_index(str(IDX_DIR / "faiss.index"))
        df = pd.read_parquet(PROC_DIR / "index_comments.parquet")
        _state = {"bm25": bm25, "faiss": index, "df": df}
    return _state


def _rows(positions, scores):
    df = _load()["df"]
    out = []
    for pos, score in zip(positions, scores):
        r = df.iloc[int(pos)]
        out.append(
            {
                "comment_id": r["id"],
                "product_id": r["product_id"],
                "product_title": r["product_title"],
                "brand": r["brand"],
                "category": r["category"],
                "text": r["text"],
                "score": float(score),
            }
        )
    return out


def search_bm25(query, k=5):
    s = _load()
    q = tokenize(normalize(query))
    scores = s["bm25"].get_scores(q)
    top = np.argsort(-scores)[:k]
    return _rows(top, scores[top])


def search_faiss(query, k=5):
    s = _load()
    resp = client.embeddings.create(model=MODEL, input=[normalize(query)])
    q = np.array([resp.data[0].embedding], dtype="float32")
    faiss.normalize_L2(q)
    scores, ids = s["faiss"].search(q, k)
    return _rows(ids[0], scores[0])

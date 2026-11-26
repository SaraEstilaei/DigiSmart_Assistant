import pandas as pd

from src.compare import load_pros_cons
from src.product_search import load_products


def list_categories(min_products=30):
    df = load_products()
    vc = df["sub_category"].fillna("نامشخص").value_counts()
    return [c for c, n in vc.items() if n >= min_products]


def _in_category(category):
    df = load_products()
    if category:
        df = df[df["sub_category"].fillna("نامشخص") == category]
    return df


def low_recommend_products(category=None, min_labeled=30, top=10):
    """محصولات پرنظر (حداقل min_labeled نظر دارای برچسب) با کمترین درصد پیشنهاد."""
    df = _in_category(category)
    df = df[df["n_labeled_comments"].fillna(0) >= min_labeled]
    df = df.sort_values("recommended_pct", ascending=True).head(top)
    cols = ["id", "title_fa", "Brand", "Price", "rate5",
            "n_labeled_comments", "recommended_pct", "not_recommended_pct"]
    return df[cols]


def brand_summary(category=None, min_products=3, top=10):
    """مقایسه‌ی برندها (برندهای عمومی/متفرقه حذف می‌شوند)."""
    df = _in_category(category)
    df = df[~df["brand_is_generic"].fillna(False)]
    g = df.groupby("Brand").agg(
        n_products=("id", "size"),
        n_labeled=("n_labeled_comments", "sum"),
        n_rec=("n_recommended", "sum"),
        avg_rate=("rate5", "mean"),
        avg_price=("Price", "mean"),
    ).reset_index()
    g = g[g["n_products"] >= min_products]
    g["recommended_pct"] = g["n_rec"] / g["n_labeled"].where(g["n_labeled"] > 0) * 100
    g = g.sort_values("n_labeled", ascending=False).head(top)
    return g[["Brand", "n_products", "n_labeled", "recommended_pct", "avg_rate", "avg_price"]]


def top_complaints(category=None, top=10):
    """پرتکرارترین معایب در یک دسته، با تعداد محصول و شناسه‌ی نظرهای نمونه."""
    ids = set(_in_category(category)["id"])
    d = load_pros_cons()
    d = d[(d["side"] == "disadvantage") & (d["product_id"].isin(ids))]
    g = d.groupby("phrase").agg(
        mentions=("count", "sum"),
        n_products=("product_id", "nunique"),
        example_comment_ids=("example_comment_ids", "first"),
    ).reset_index()
    g = g.sort_values(["mentions", "n_products"], ascending=False).head(top)
    g["example_comment_ids"] = g["example_comment_ids"].apply(lambda x: [int(i) for i in x])
    return g

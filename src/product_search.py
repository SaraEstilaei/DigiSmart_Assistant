import pandas as pd

from src.ranking import add_bayesian_score

PRODUCTS_PATH = "data/processed/sample_products_3k.parquet"
_cache = {}


def load_products():
    if "df" not in _cache:
        df = pd.read_parquet(PRODUCTS_PATH)
        _cache["df"] = add_bayesian_score(df, m=20)
    return _cache["df"]


def search_products(query="", filters=None, top_k=10):
    """فیلتر ساخت‌یافته + رتبه‌بندی با امتیاز بیزی.

    filters (همه اختیاری):
      category: متن داخل Category1 یا sub_category
      brand: متن داخل Brand
      min_price, max_price: بازه‌ی قیمت (تومان)
      min_rate: حداقل امتیاز در مقیاس 0 تا 5
      min_votes: حداقل تعداد امتیاز
    query: اگر داده شود، در عنوان محصول جست‌وجو می‌شود.
    """
    filters = filters or {}
    df = load_products()
    df = df[~df["Is_Fake"].fillna(False)]
    df = df[~df["price_is_extreme"].fillna(False)]

    if filters.get("category"):
        c = filters["category"]
        mask = df["Category1"].fillna("").str.contains(c, regex=False) | \
               df["sub_category"].fillna("").str.contains(c, regex=False)
        df = df[mask]
    if filters.get("brand"):
        df = df[df["Brand"].fillna("").str.contains(filters["brand"], regex=False)]
    if filters.get("min_price") is not None:
        df = df[df["Price"] >= filters["min_price"]]
    if filters.get("max_price") is not None:
        df = df[df["Price"] <= filters["max_price"]]
    if filters.get("min_rate") is not None:
        df = df[df["rate5"] >= filters["min_rate"]]
    if filters.get("min_votes") is not None:
        df = df[df["Rate_cnt"] >= filters["min_votes"]]
    if query:
        df = df[df["title_fa"].fillna("").str.contains(query, regex=False)]

    df = df.sort_values("bayes_score", ascending=False).head(top_k)
    cols = ["id", "title_fa", "Brand", "Price", "rate5", "Rate_cnt", "bayes_score"]
    return df[cols].to_dict(orient="records")

import pandas as pd

from src.llm_cache import cached_chat
from src.product_search import load_products

PROS_CONS_PATH = "data/processed/product_pros_cons.parquet"
_pc = {}


def load_pros_cons():
    if "df" not in _pc:
        _pc["df"] = pd.read_parquet(PROS_CONS_PATH)
    return _pc["df"]


def get_evidence(product_id, top=3):
    """مزایا/معایب پرتکرار یک محصول، با تعداد تکرار و شناسه‌ی نظرهای نمونه."""
    d = load_pros_cons()
    d = d[d["product_id"] == product_id]
    out = {"advantages": [], "disadvantages": []}
    for side, key in [("advantage", "advantages"), ("disadvantage", "disadvantages")]:
        part = d[d["side"] == side].sort_values("count", ascending=False).head(top)
        for _, r in part.iterrows():
            out[key].append({
                "phrase": r["phrase"],
                "count": int(r["count"]),
                "comment_ids": [int(i) for i in r["example_comment_ids"]],
            })
    return out


def compare_table(product_ids):
    """جدول مقایسه‌ی ساخت‌یافته با کد (بدون LLM)."""
    df = load_products()
    rows = df[df["id"].isin(product_ids)].copy()
    cols = ["id", "title_fa", "Brand", "Price", "rate5", "Rate_cnt", "bayes_score",
            "n_labeled_comments", "recommended_pct"]
    rows = rows[cols].sort_values("bayes_score", ascending=False)
    records = rows.to_dict(orient="records")

    facts = {}
    if records:
        facts["cheapest"] = min(records, key=lambda r: r["Price"])["id"]
        facts["best_rated"] = max(records, key=lambda r: r["bayes_score"])["id"]
        facts["most_reviewed"] = max(records, key=lambda r: r["Rate_cnt"])["id"]
    return {"table": records, "facts": facts}


SYSTEM_PROMPT = """تو دستیار مقایسه‌ی محصولات یک فروشگاه اینترنتی هستی.
فقط از اطلاعات داده‌شده استفاده کن و هیچ ویژگی یا ادعای دیگری از خودت نساز.
قیمت‌ها به تومان و امتیاز از ۰ تا ۵ است. «درصد پیشنهاد» یعنی چند درصد از نظرهای دارای برچسب، خرید محصول را پیشنهاد کرده‌اند (با تعداد نظر دارای برچسب).
پاسخ را دقیقاً در سه بخش بنویس:
1) داده مستقیم: اعداد جدول (قیمت، امتیاز، تعداد امتیاز، درصد پیشنهاد) به‌صورت خلاصه.
2) شواهد نظرات: فقط از مزایا و معایب پرتکرار داده‌شده استفاده کن. هر مورد را با تعداد تکرار و شناسه‌ی نظرها (comment_id) بنویس. برای محصولی که مورد پرتکرار ندارد بنویس «مورد پرتکرار پیدا نشد».
3) استنتاج: پیشنهاد کوتاه تو برای کاربر، با دلیل. این بخش را با برچسب «استنتاج» شروع کن و بگو بر چه اساسی است.
درباره‌ی کاربرد، جنس، کیفیت یا ویژگی‌هایی که در داده‌ها نیست هیچ ادعایی نکن. اگر اطلاعات کافی برای قضاوت نیست، صریح بگو."""


def _fmt_items(items):
    if not items:
        return "مورد پرتکرار پیدا نشد"
    return "؛ ".join(
        f"{i['phrase']} ({i['count']} نفر، comment_id: {', '.join(map(str, i['comment_ids']))})"
        for i in items
    )


def compare(product_ids, query=""):
    """مقایسه: جدول با کد + شواهد نظرات + جمع‌بندی LLM با تفکیک داده/شواهد/استنتاج."""
    result = compare_table(product_ids)
    if not result["table"]:
        return {**result, "summary": "هیچ محصولی با این شناسه‌ها پیدا نشد."}

    evidence = {r["id"]: get_evidence(r["id"]) for r in result["table"]}
    result["evidence"] = evidence

    user_msg = f"نیاز کاربر: {query or 'مقایسه‌ی عمومی'}\n\nمحصولات:\n"
    for r in result["table"]:
        pct = r["recommended_pct"]
        pct_txt = "نامشخص" if pd.isna(pct) else f"{pct:.0f}٪ (از {int(r['n_labeled_comments'])} نظر دارای برچسب)"
        ev = evidence[r["id"]]
        user_msg += (
            f"- id={r['id']} | {r['title_fa']} | برند: {r['Brand']} | "
            f"قیمت: {int(r['Price']):,} تومان | امتیاز: {r['rate5']:.1f} | "
            f"تعداد امتیاز: {r['Rate_cnt']} | درصد پیشنهاد: {pct_txt}\n"
            f"    مزایای پرتکرار: {_fmt_items(ev['advantages'])}\n"
            f"    معایب پرتکرار: {_fmt_items(ev['disadvantages'])}\n"
        )
    text, from_cache = cached_chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        model="openai/gpt-4o-mini",
        task="compare",
        temperature=0.2,
        max_tokens=900,
    )
    return {**result, "summary": text, "from_cache": from_cache}



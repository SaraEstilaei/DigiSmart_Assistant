import json
import re

from src.llm_cache import cached_chat
from src.product_search import search_products

CATEGORIES = ["beauty", "book & stationary & art", "clothe",
              "toys and kids", "rural goods", "travel"]

PARSE_PROMPT = """از پیام کاربر فقط این فیلدها را به‌صورت JSON خالص (بدون هیچ متن دیگر) بنویس:
{"keyword": ..., "category": ..., "max_price": ..., "min_price": ..., "min_rate": ..., "brand": ...}
- keyword: یک کلمه‌ی ساده برای نوع محصول که در عنوان محصول می‌آید (مثلاً «کیف»)، وگرنه null.
- category: یکی از این مقادیر یا null: beauty, book & stationary & art, clothe, toys and kids, rural goods, travel
- max_price و min_price: به تومان و فقط اگر کاربر عدد یا بازه گفته (مثلاً «زیر یک میلیون» یعنی 1000000)، وگرنه null.
- min_rate: عدد ۰ تا ۵ فقط اگر کاربر صریحاً حداقل امتیاز خواسته، وگرنه null.
- brand: فقط اگر کاربر نام برند گفته، وگرنه null.
چیزی را از خودت حدس نزن."""

ANSWER_PROMPT = """تو دستیار خرید یک فروشگاه اینترنتی هستی.
فقط از فهرست محصولات داده‌شده استفاده کن و هیچ ویژگی یا ادعای دیگری از خودت نساز.
قیمت‌ها به تومان و امتیاز از ۰ تا ۵ است. درصد پیشنهاد یعنی چند درصد از نظرهای دارای برچسب، خرید را پیشنهاد کرده‌اند.
در ۳ تا ۴ جمله بگو کدام محصول‌ها به نیاز کاربر نزدیک‌ترند و چرا (فقط بر اساس قیمت، امتیاز و درصد پیشنهاد).
اگر نوع محصول از روی عنوان با درخواست کاربر نمی‌خواند، آن را کنار بگذار و کوتاه بگو چرا.
اگر کاربر عدد قیمتی نگفته، درباره‌ی گران یا ارزان بودن نسبت به انتظار او قضاوت نکن و فقط قیمت‌ها را بگو.
درباره‌ی کاربرد، جنس یا کیفیتی که از عنوان و اعداد فهرست معلوم نیست ادعا نکن. محصولی را فقط به خاطر «نوع کاربرد» رد نکن؛ اگر به نظرت مناسب نیست بگو «از روی داده نمی‌شود فهمید»."""


def parse_query(text):
    out, _ = cached_chat(
        [{"role": "system", "content": PARSE_PROMPT},
         {"role": "user", "content": text}],
        model="openai/gpt-4o-mini", task="parse_query",
        temperature=0, max_tokens=200,
    )
    m = re.search(r"\{.*\}", out, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def build_filters(d):
    f = {"min_votes": 20}
    if d.get("category") in CATEGORIES:
        f["category"] = d["category"]
    for k in ("max_price", "min_price", "min_rate"):
        v = d.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            f[k] = v
    if d.get("brand"):
        f["brand"] = d["brand"]
    return f


def chat_answer(text, top_k=5):
    parsed = parse_query(text)
    keys = ("keyword", "category", "max_price", "min_price", "min_rate", "brand")
    if not any(parsed.get(k) for k in keys):
        return {"parsed": parsed, "filters": {}, "results": [], "relaxed": False,
                "answer": "نوع محصول مورد نظرت را متوجه نشدم. لطفاً بنویس دنبال چه چیزی هستی (مثلاً کیف، کتاب کودک یا لوازم آرایشی) و در صورت نیاز بازه‌ی قیمت."}
    filters = build_filters(parsed)
    kw = parsed.get("keyword") or ""
    results = search_products(kw, filters, top_k=top_k)
    relaxed = False
    if len(results) < top_k and kw and "category" in filters:
        f2 = {k: v for k, v in filters.items() if k != "category"}
        extra = search_products(kw, f2, top_k=top_k)
        seen = {r["id"] for r in results}
        results = results + [r for r in extra if r["id"] not in seen]
        results = sorted(results, key=lambda r: r["final_score"], reverse=True)[:top_k]
        relaxed = True
    if not results:
        return {"parsed": parsed, "filters": filters, "results": [], "relaxed": relaxed,
                "answer": "محصولی با این شرایط پیدا نشد. شرایط را کمی شل‌تر کن."}

    lines = []
    for r in results:
        pct = r["recommended_pct"]
        pct_txt = "نامشخص" if pct != pct else f"{pct:.0f}٪ (از {int(r['n_labeled_comments'])} نظر)"
        lines.append(f"- id={r['id']} | {r['title_fa']} | قیمت: {int(r['Price']):,} تومان | "
                     f"امتیاز: {r['rate5']:.1f} | تعداد امتیاز: {r['Rate_cnt']} | درصد پیشنهاد: {pct_txt}")
    msg = f"نیاز کاربر: {text}\n\nفهرست محصولات:\n" + "\n".join(lines)
    answer, _ = cached_chat(
        [{"role": "system", "content": ANSWER_PROMPT}, {"role": "user", "content": msg}],
        model="openai/gpt-4o-mini", task="chat_answer", temperature=0.2, max_tokens=400,
    )
    return {"parsed": parsed, "filters": filters, "results": results,
            "relaxed": relaxed, "answer": answer}

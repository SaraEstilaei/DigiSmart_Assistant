from src.product_search import load_products


def compare_table(product_ids):
    """جدول مقایسه‌ی ساخت‌یافته با کد (بدون LLM)."""
    df = load_products()
    rows = df[df["id"].isin(product_ids)].copy()
    cols = ["id", "title_fa", "Brand", "Price", "rate5", "Rate_cnt", "bayes_score"]
    rows = rows[cols].sort_values("bayes_score", ascending=False)
    records = rows.to_dict(orient="records")

    facts = {}
    if records:
        facts["cheapest"] = min(records, key=lambda r: r["Price"])["id"]
        facts["best_rated"] = max(records, key=lambda r: r["bayes_score"])["id"]
        facts["most_reviewed"] = max(records, key=lambda r: r["Rate_cnt"])["id"]
    return {"table": records, "facts": facts}


from src.llm_cache import cached_chat

SYSTEM_PROMPT = """تو دستیار مقایسه‌ی محصولات یک فروشگاه اینترنتی هستی.
فقط از اطلاعات جدولی که به تو داده می‌شود استفاده کن و هیچ ویژگی یا ادعای دیگری از خودت نساز.
قیمت‌ها به تومان و امتیاز از ۰ تا ۵ است. Rate_cnt تعداد امتیازهای ثبت‌شده است.
پاسخ را دقیقاً در سه بخش بنویس:
1) داده مستقیم: اعداد جدول (قیمت، امتیاز، تعداد امتیاز) به‌صورت خلاصه.
2) شواهد نظرات: بنویس «در این نسخه، نظرات کاربران برای این مقایسه در دسترس نیست.»
3) استنتاج: پیشنهاد کوتاه تو برای کاربر، با دلیل. این بخش را با برچسب «استنتاج» شروع کن و بگو بر چه اساسی است.
درباره‌ی کاربرد، جنس، کیفیت یا ویژگی‌هایی که در جدول نیست هیچ ادعایی نکن؛ فقط بر اساس قیمت، امتیاز و تعداد امتیاز نتیجه بگیر. اگر اطلاعات کافی برای قضاوت نیست، صریح بگو."""


def compare(product_ids, query=""):
    """مقایسه: جدول با کد + جمع‌بندی LLM با تفکیک داده/شواهد/استنتاج."""
    result = compare_table(product_ids)
    if not result["table"]:
        return {**result, "summary": "هیچ محصولی با این شناسه‌ها پیدا نشد."}

    user_msg = f"نیاز کاربر: {query or 'مقایسه‌ی عمومی'}\n\nجدول محصولات:\n"
    for r in result["table"]:
        user_msg += (
            f"- id={r['id']} | {r['title_fa']} | برند: {r['Brand']} | "
            f"قیمت: {int(r['Price']):,} تومان | امتیاز: {r['rate5']:.1f} | "
            f"تعداد امتیاز: {r['Rate_cnt']}\n"
        )
    text, from_cache = cached_chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        model="openai/gpt-4o-mini",
        task="compare",
        temperature=0.2,
        max_tokens=600,
    )
    return {**result, "summary": text, "from_cache": from_cache}




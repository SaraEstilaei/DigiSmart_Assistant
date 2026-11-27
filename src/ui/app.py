import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from src.chat import chat_answer
from src.compare import compare
from src.manager import brand_summary, list_categories, low_recommend_products, top_complaints
from src.product_search import search_products

CAT_FA = {
    "beauty": "زیبایی و سلامت", "book & stationary & art": "کتاب، لوازم‌التحریر و هنر",
    "clothe": "پوشاک", "toys and kids": "اسباب‌بازی و کودک",
    "rural goods": "لوازم خانه", "travel": "سفر",
}

COLS = {
    "id": "شناسه", "title_fa": "عنوان", "Brand": "برند",
    "Price": "قیمت (تومان)", "rate5": "امتیاز (از ۵)",
    "Rate_cnt": "تعداد امتیاز", "bayes_score": "امتیاز بیزی",
    "n_labeled_comments": "نظر دارای برچسب",
    "recommended_pct": "درصد پیشنهاد", "final_score": "امتیاز نهایی",
}


def pretty(records):
    df = pd.DataFrame(records)
    for c in ["rate5", "bayes_score"]:
        if c in df:
            df[c] = df[c].round(2)
    if "final_score" in df:
        df["final_score"] = df["final_score"].round(3)
    if "recommended_pct" in df:
        df["recommended_pct"] = df["recommended_pct"].round(0)
    return df.rename(columns=COLS)


def show_items(items):
    if not items:
        st.write("مورد پرتکرار پیدا نشد")
    for i in items:
        ids = "، ".join(str(x) for x in i["comment_ids"])
        st.write(f"- {i['phrase']} ({i['count']} نفر) — شناسه‌ی نظرها: {ids}")


st.set_page_config(page_title="دستیار خرید دیجی‌کالا", page_icon="🛒", layout="wide")
st.markdown(
    "<style>html, body, [class*='css'] {direction: rtl; text-align: right;}</style>",
    unsafe_allow_html=True,
)
st.title("🛒 دستیار هوشمند خرید")

tab_chat, tab_search, tab_compare, tab_manager = st.tabs(["💬 دستیار", "🔍 جست‌وجوی محصول", "⚖️ مقایسه", "📊 تحلیل مدیر"])

with tab_search:
    st.subheader("جست‌وجو با فیلتر")
    c1, c2 = st.columns(2)
    query = c1.text_input("کلمه‌ی کلیدی در عنوان (مثلاً: کیف)")
    category = c2.text_input("دسته‌بندی (اختیاری)")
    c3, c4, c5 = st.columns(3)
    max_price = c3.number_input("حداکثر قیمت (تومان)", min_value=0, value=0, step=50000)
    min_rate = c4.slider("حداقل امتیاز (از ۵)", 0.0, 5.0, 0.0, 0.1)
    min_votes = c5.number_input("حداقل تعداد امتیاز", min_value=0, value=0, step=5)

    if st.button("جست‌وجو", type="primary"):
        filters = {"min_rate": min_rate, "min_votes": min_votes}
        if category:
            filters["category"] = category
        if max_price > 0:
            filters["max_price"] = max_price
        st.session_state["results"] = search_products(query, filters, top_k=10)

    results = st.session_state.get("results")
    if results is not None:
        if not results:
            st.warning("محصولی با این شرایط پیدا نشد. فیلترها را شل‌تر کن.")
        else:
            st.dataframe(pretty(results), use_container_width=True, hide_index=True)
            st.caption("درصد پیشنهاد فقط روی نظرهای دارای برچسب حساب شده. شناسه‌ها را برای مقایسه در تب بعدی استفاده کن.")

with tab_compare:
    st.subheader("مقایسه‌ی محصولات")
    ids_text = st.text_input("شناسه‌ی محصولات (با کاما جدا کن)", placeholder="2829072, 7294595, 4260784")
    need = st.text_input("نیاز تو (اختیاری)", placeholder="یک کیف ارزان برای استفاده روزمره")

    if st.button("مقایسه کن"):
        try:
            ids = [int(x.strip()) for x in ids_text.split(",") if x.strip()]
        except ValueError:
            ids = []
        if len(ids) < 2:
            st.warning("حداقل دو شناسه‌ی معتبر وارد کن.")
        else:
            with st.spinner("در حال مقایسه..."):
                try:
                    out = compare(ids, need)
                except Exception:
                    st.error("سرویس مدل زبانی پاسخ نداد. اینترنت و کلید API را چک کن و دوباره امتحان کن.")
                    st.stop()
            if out["table"]:
                st.dataframe(pretty(out["table"]), use_container_width=True, hide_index=True)
                for r in out["table"]:
                    ev = out["evidence"][r["id"]]
                    with st.expander("شواهد نظرات: " + r["title_fa"]):
                        st.markdown("**مزایای پرتکرار**")
                        show_items(ev["advantages"])
                        st.markdown("**معایب پرتکرار**")
                        show_items(ev["disadvantages"])
            st.markdown(out["summary"])
            st.caption("از کش خوانده شد ⚡" if out.get("from_cache") else "از مدل زبانی گرفته شد")




with tab_manager:
    st.subheader("تحلیل دسته برای مدیر فروشگاه")
    cats = list_categories()
    cat = st.selectbox("دسته", cats, format_func=lambda c: CAT_FA.get(c, c))
    min_lab = st.slider("حداقل تعداد نظر دارای برچسب (برای محصولات پرنظر)", 10, 200, 30, 10)

    st.markdown("### ⚠️ محصولات پرنظر با درصد پیشنهاد پایین")
    lr = low_recommend_products(cat, min_labeled=min_lab, top=10)
    st.dataframe(pretty(lr.to_dict(orient="records")), use_container_width=True, hide_index=True)

    st.markdown("### 🏷️ مقایسه‌ی برندها")
    bs = brand_summary(cat, top=10).rename(columns={
        "Brand": "برند", "n_products": "تعداد محصول", "n_labeled": "نظر دارای برچسب",
        "recommended_pct": "درصد پیشنهاد", "avg_rate": "میانگین امتیاز", "avg_price": "میانگین قیمت"})
    st.dataframe(bs.round(1), use_container_width=True, hide_index=True)

    st.markdown("### 😕 پرتکرارترین شکایت‌ها")
    tc = top_complaints(cat, top=10).rename(columns={
        "phrase": "شکایت", "mentions": "تعداد ذکر", "n_products": "تعداد محصول",
        "example_comment_ids": "شناسه‌ی نظرهای نمونه"})
    if tc.empty:
        st.info("برای این دسته شکایت پرتکرار پیدا نشد.")
    else:
        st.dataframe(tc, use_container_width=True, hide_index=True)
    st.caption("همه‌ی اعداد از نظرات واقعی با کد حساب شده‌اند (بدون مدل زبانی).")


with tab_chat:
    st.subheader("نیازت رو به فارسی بنویس")
    q = st.text_area("مثلاً: یک کیف برای استفاده روزمره می‌خوام که خیلی گرون نباشه و خریدارها هم ازش راضی باشن", height=90)
    if st.button("پیشنهاد بده", type="primary") and q.strip():
        with st.spinner("در حال جست‌وجو..."):
            try:
                st.session_state["chat_out"] = chat_answer(q.strip())
            except Exception:
                st.error("سرویس مدل زبانی پاسخ نداد. اینترنت و کلید API را چک کن و دوباره امتحان کن.")
                st.stop()
    out = st.session_state.get("chat_out")
    if out:
        st.markdown(out["answer"])
        if out["results"]:
            st.dataframe(pretty(out["results"]), use_container_width=True, hide_index=True)
        with st.expander("فیلترهای استخراج‌شده از پرسش"):
            st.json(out["parsed"])
        if out.get("relaxed"):
            st.caption("چون نتیجه‌ها با دسته‌ی حدس‌زده‌شده کم بود، بدون دسته هم جست‌وجو شد.")

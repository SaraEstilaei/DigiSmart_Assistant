import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from src.compare import compare
from src.product_search import load_products, search_products

st.set_page_config(page_title="دستیار خرید دیجی‌کالا", page_icon="🛒", layout="wide")
st.markdown(
    "<style>html, body, [class*='css'] {direction: rtl; text-align: right;}</style>",
    unsafe_allow_html=True,
)
st.title("🛒 دستیار هوشمند خرید")

tab_search, tab_compare = st.tabs(["🔍 جست‌وجوی محصول", "⚖️ مقایسه"])

# ---------- تب جست‌وجو ----------
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
        results = search_products(query, filters, top_k=10)
        st.session_state["results"] = results

    results = st.session_state.get("results")
    if results is not None:
        if not results:
            st.warning("محصولی با این شرایط پیدا نشد. فیلترها را شل‌تر کن.")
        else:
            df = pd.DataFrame(results)
            df = df.rename(columns={
                "id": "شناسه", "title_fa": "عنوان", "Brand": "برند",
                "Price": "قیمت (تومان)", "rate5": "امتیاز (از ۵)",
                "Rate_cnt": "تعداد امتیاز", "bayes_score": "امتیاز بیزی",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption("شناسه‌ی محصولات را برای مقایسه در تب بعدی استفاده کن.")

# ---------- تب مقایسه ----------
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
                out = compare(ids, need)
            if out["table"]:
                tdf = pd.DataFrame(out["table"]).rename(columns={
                    "id": "شناسه", "title_fa": "عنوان", "Brand": "برند",
                    "Price": "قیمت (تومان)", "rate5": "امتیاز (از ۵)",
                    "Rate_cnt": "تعداد امتیاز", "bayes_score": "امتیاز بیزی",
                })
                st.dataframe(tdf, use_container_width=True, hide_index=True)
            st.markdown(out["summary"])
            st.caption("از کش خوانده شد ⚡" if out.get("from_cache") else "از مدل زبانی گرفته شد")

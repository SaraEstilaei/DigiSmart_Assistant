p = "src/ui/app.py"
s = open(p, encoding="utf-8").read()
assert "chat_answer" not in s, "تب چت قبلاً اضافه شده"

old_tabs = 'tab_search, tab_compare, tab_manager = st.tabs(["🔍 جست‌وجوی محصول", "⚖️ مقایسه", "📊 تحلیل مدیر"])'
new_tabs = 'tab_chat, tab_search, tab_compare, tab_manager = st.tabs(["💬 دستیار", "🔍 جست‌وجوی محصول", "⚖️ مقایسه", "📊 تحلیل مدیر"])'
assert old_tabs in s, "خط تب‌ها پیدا نشد"
s = s.replace(old_tabs, new_tabs)
s = s.replace("from src.compare import compare", "from src.chat import chat_answer\nfrom src.compare import compare", 1)

s += """

with tab_chat:
    st.subheader("نیازت رو به فارسی بنویس")
    q = st.text_area("مثلاً: یک کیف برای استفاده روزمره می‌خوام که خیلی گرون نباشه و خریدارها هم ازش راضی باشن", height=90)
    if st.button("پیشنهاد بده", type="primary") and q.strip():
        with st.spinner("در حال جست‌وجو..."):
            st.session_state["chat_out"] = chat_answer(q.strip())
    out = st.session_state.get("chat_out")
    if out:
        st.markdown(out["answer"])
        if out["results"]:
            st.dataframe(pretty(out["results"]), use_container_width=True, hide_index=True)
        with st.expander("فیلترهای استخراج‌شده از پرسش"):
            st.json(out["filters"])
        if out.get("relaxed"):
            st.caption("چون با دسته‌ی انتخاب‌شده نتیجه‌ای نبود، دسته نادیده گرفته شد.")
"""
open(p, "w", encoding="utf-8").write(s)
print("OK")

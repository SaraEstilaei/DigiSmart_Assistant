import streamlit as st

st.set_page_config(page_title="دستیار خرید دیجی‌کالا", page_icon="🛒")
st.title("🛒 دستیار هوشمند خرید")

# تاریخچه‌ی چت را نگه می‌داریم
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# گرفتن پرسش جدید
query = st.chat_input("نیازت رو بنویس...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    reply = "فعلا فقط اسکلت UI آماده است. بعدا به جست‌وجو وصل می‌شود."
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

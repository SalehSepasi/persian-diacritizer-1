import streamlit as st
from persian_diacritizer import diacritize

st.set_page_config(page_title="اعراب‌گذاری", page_icon="✒️")

st.markdown(
    "<style>textarea, .stMarkdown {direction: rtl; text-align: right;}</style>",
    unsafe_allow_html=True,
)

st.title("✒️ اعراب‌گذاری متن فارسی")

text = st.text_area("متن را وارد کنید", height=150)

if st.button("اعراب‌گذاری کن", type="primary") and text.strip():
    st.success(diacritize(text))
import streamlit as st

from persian_diacritizer import diacritize


text = st.chat_input()
result = diacritize(text)
st.write(result)




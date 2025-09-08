import streamlit as st


pages = [
    st.Page("pages/Main.py", title="Main"),
    st.Page("pages/ListVocabs.py", title="My Vocabulary"),
    st.Page("pages/AddWords.py", title="Add New Words"),
]

pg = st.navigation(pages)
pg.run()


import streamlit as st
from gc_translate_utils import GCTranslateUtils


st.set_page_config(
    page_title="Word Finder",
)

st.title("Welcome to Word Finder!")

st.markdown("""      
    This is English Vocabulary Application for the intermediate students.     
    Create your own English Vocabulary List with Word Finder.
""")

st.divider()

st.subheader("Enrolled Today")
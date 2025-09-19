import streamlit as st
from gc_translate_utils import GCTranslateUtils
from datetime import date


def set_background_color(_):
    return "font-weight: bold; background-color: yellow;"

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

vocab_df = st.session_state["vocab_df"]
today = str(date.today())
today_vocab = vocab_df[vocab_df["search_date"]==today].reset_index(drop=True)

if len(today_vocab) != 0:
    today_vocab = today_vocab[["word", "pronunciation", "meaning", "note"]]
    styled_df = today_vocab.style.map(set_background_color, subset=["word"])
    st.dataframe(styled_df, hide_index=True)

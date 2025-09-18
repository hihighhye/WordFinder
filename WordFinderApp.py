import streamlit as st
import database_utils as db
from googlesheets_utils import GooglesheetUtils
from datetime import date
import pandas as pd


@st.dialog("Settings")
def set_up():
    st.text_input("Language to learn", value="English", disabled=True)
    native_lang = st.selectbox(
        "Native language",
        st.session_state["lang_options"],
    )
    if st.button("save"):
        st.session_state["native_lang"] = native_lang
        st.rerun()

@st.cache_resource(show_spinner="Loading your vocab...")
def get_resource():
    googlesheet = GooglesheetUtils(spreadsheet_id="1hFNuCdmySJodQM5qsR5FJ6pkPLQc5DbXwP7h74pwTs8")

    values = googlesheet.get_data("Behave!B5:H")

    vocab_df = pd.DataFrame(values)
    vocab_df.columns = ["cat1", "cat2", "word", "pronunciation", "meaning", "note", "example"]
    # vocab_df["Cat2"] = vocab_df["Cat2"].apply(lambda x: "Etc" if not x or x == "" else x)
    vocab_df = vocab_df.fillna("")
    return vocab_df

@st.cache_resource(show_spinner="Loading your vocab...")
def load_data():
    db.initialize_db()
    current_data = db.get_data()
    if not current_data:
        sample_vocab = get_resource()
        init_date = date.today()

        records = []
        for row in sample_vocab.itertuples():
            row = row[1:]
            records.append((*row, init_date))
        db.insert_data(records)
        current_data = db.get_data()

    vocab_df = pd.DataFrame(current_data, columns=[
        "cat1", "cat2", "word", "pronunciation", "meaning", 
        "note", "example", "star", "search_date"]
    )
    return vocab_df

st.session_state["lang_options"] = [
    "Korean",
    "Amharic",
    "Arabic",
    "Basque",
    "Bengali",
    "Portuguese (Brazil)",
    "Bulgarian",
    "Catalan",
    "Cherokee",
    "Croatian",
    "Czech",
    "Danish",
    "Dutch",
    "Estonian",
    "Filipino",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Gujarati",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Indonesian",
    "Italian",
    "Japanese",
    "Kannada",
    "Latvian",
    "Lithuanian",
    "Malay",
    "Malayalam",
    "Marathi",
    "Norwegian",
    "Polish",
    "Portuguese (Portugal)",
    "Romanian",
    "Russian",
    "Serbian",
    "Chinese (PRC)",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swahili",
    "Swedish",
    "Tamil",
    "Telugu",
    "Thai",
    "Chinese (Taiwan)",
    "Turkish",
    "Urdu",
    "Ukrainian",
    "Vietnamese",
    "Welsh"
]

if "native_lang" not in st.session_state.keys():
    st.session_state["native_lang"] = "Korean"

if "vocab_df" not in st.session_state.keys():
    st.session_state["vocab_df"] = load_data()

pages = [
    st.Page("pages/Main.py", title="Main", icon=":material/home:"),
    st.Page("pages/ListVocabs.py", title="My Vocabulary", icon=":material/hive:"),
    st.Page("pages/AddWords.py", title="Add New Words", icon=":material/list_alt_add:"),
]

pg = st.navigation(pages)
pg.run()

with st.sidebar:
    if st.button(":material/settings: Settings"):
        set_up()
 
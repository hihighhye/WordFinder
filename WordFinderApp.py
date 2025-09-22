import streamlit as st
import database_utils as db
from googlesheets_utils import GooglesheetUtils
from datetime import date
import pandas as pd
from crews.wordsfinder_crew import WordsFinderCrew


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
        sample_vocab = sample_vocab.sample(frac=1, random_state=42).reset_index(drop=True)
        sample_vocab = sample_vocab[:30]
        init_date = "2025-09-01" # date.today()

        records = []
        for row in sample_vocab.itertuples():
            row = row[1:]
            records.append((*row, '', init_date))
        db.insert_data(records)
        current_data = db.get_data()

    vocab_df = pd.DataFrame(current_data, columns=[
        "cat1", "cat2", "word", "pronunciation", "meaning", 
        "note", "example", "star", "img", "search_date"]
    )
    return vocab_df

@st.cache_resource()
def create_wf_crew(native_lang):
    st.session_state["wordfinder_crew"] = WordsFinderCrew(native_lang=native_lang)
    print("Created new WF Crew!")
    return st.session_state["wordfinder_crew"]

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
    vocab_df = load_data()
    st.session_state["vocab_df"] = vocab_df

wordfinder_crew = create_wf_crew(st.session_state["native_lang"])
st.session_state["wordfinder_crew"] = wordfinder_crew

pages = [
    st.Page("pages/Main.py", title="Main", icon=":material/home:"),
    st.Page("pages/AddWords.py", title="Add New Words", icon=":material/list_alt_add:"),
    st.Page("pages/ListVocabs.py", title="My Vocabulary", icon=":material/hive:"),
    st.Page("pages/Translator.py", title="Translator", icon=":material/convert_to_text:"),
    st.Page("pages/Quiz.py", title="Quiz", icon=":material/crossword:"),
]

pg = st.navigation(pages)
pg.run()

with st.sidebar:
    if st.button(":material/settings: Settings"):
        set_up()
 
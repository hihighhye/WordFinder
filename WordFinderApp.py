import streamlit as st
import database_utils as db
# from googlesheets_utils import GooglesheetUtils
from datetime import date
import pandas as pd
from crews.wordsfinder_crew import WordsFinderCrew
from crews.translator_crew import TranslatorCrew
import os
from openai import OpenAI
import gc_translate_utils as gct
from langchain.chat_models import ChatOpenAI


def test_api_key_validation(openai_api_key):
    return OpenAI(api_key=openai_api_key).chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":"ping"}]
    )

def get_display_name_by_lang_code(lang_code):
    lang_idx = [lang.language_code for lang in st.session_state["lang_options"]].index(lang_code)
    return st.session_state["lang_options"][lang_idx].display_name

@st.dialog("Settings")
def set_up():
    user_openai_api_key = st.text_input(
        "*Your OpenAI API key (Requirement)", 
        value=st.session_state["user_openai_api_key"] if "user_openai_api_key" in st.session_state else None
    )

    default_lang_index = [lang.language_code for lang in st.session_state["lang_options"]].index(st.session_state["native_lang_code"]) if "native_lang_code" in st.session_state else ""
        
    target_lang = st.text_input("Language to learn", value="English", disabled=True)
    native_lang_code = st.selectbox(
        "Native language",
        options=[lang.language_code for lang in st.session_state["lang_options"]],
        format_func=get_display_name_by_lang_code,
        index=default_lang_index,
    )

    # image_on = st.toggle(
    #     "Visualize words (experimental)", 
    #     value=st.session_state["image_on"] if "image_on" in st.session_state else False,
    #     # disabled=True
    # )

    if st.button("save"):
        user_openai_api_key = user_openai_api_key.strip() if user_openai_api_key else None
        if user_openai_api_key:   
            try:
                res = test_api_key_validation(user_openai_api_key)
        
                st.session_state["user_openai_api_key"] = user_openai_api_key
                st.session_state["native_lang_code"] = native_lang_code
                # st.session_state["image_on"] = image_on
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error("Please enter valid OpenAI API key.")
                st.session_state.pop("user_openai_api_key", None)

        else:
            st.error("Please enter valid OpenAI API key.")
            st.session_state.pop("user_openai_api_key", None)

# @st.cache_resource(show_spinner="Loading your vocab...")
# def get_resource():
#     googlesheet = GooglesheetUtils(spreadsheet_id="1hFNuCdmySJodQM5qsR5FJ6pkPLQc5DbXwP7h74pwTs8")

#     values = googlesheet.get_data("Behave!B5:H")

#     vocab_df = pd.DataFrame(values)
#     vocab_df.columns = ["cat1", "cat2", "word", "pronunciation", "meaning", "note", "example"]
#     vocab_df = vocab_df.fillna("")
#     return vocab_df

@st.cache_resource(show_spinner="Loading your vocab...")
def load_data():
    db.initialize_db()
    current_data = db.get_data()
    #############################################################################
    # Load Sample Data
    #############################################################################
    # if not current_data:
    #     sample_vocab = get_resource()
    #     sample_vocab = sample_vocab.sample(frac=1, random_state=42).reset_index(drop=True)
    #     sample_vocab = sample_vocab[:30]
    #     init_date = "2025-10-01" # date.today()

    #     records = []
    #     for row in sample_vocab.itertuples():
    #         row = row[1:]
    #         records.append((*row, '', '', '', init_date)) # added synonym, antonym, img, search_date
    #     db.insert_data(records)
    #     current_data = db.get_data()
    ############################################################################

    vocab_df = pd.DataFrame(current_data, columns=[
        "cat1", "cat2", "word", "pronunciation", "meaning", 
        "note", "example", "star", "synonym", "antonym" , "img", "search_date"]
    )
    return vocab_df

# st.session_state["lang_options"] = [
#     "Korean",
#     "Amharic",
#     "Arabic",
#     "Basque",
#     "Bengali",
#     "Portuguese (Brazil)",
#     "Bulgarian",
#     "Catalan",
#     "Cherokee",
#     "Croatian",
#     "Czech",
#     "Danish",
#     "Dutch",
#     "Estonian",
#     "Filipino",
#     "Finnish",
#     "French",
#     "German",
#     "Greek",
#     "Gujarati",
#     "Hebrew",
#     "Hindi",
#     "Hungarian",
#     "Icelandic",
#     "Indonesian",
#     "Italian",
#     "Japanese",
#     "Kannada",
#     "Latvian",
#     "Lithuanian",
#     "Malay",
#     "Malayalam",
#     "Marathi",
#     "Norwegian",
#     "Polish",
#     "Portuguese (Portugal)",
#     "Romanian",
#     "Russian",
#     "Serbian",
#     "Chinese (PRC)",
#     "Slovak",
#     "Slovenian",
#     "Spanish",
#     "Swahili",
#     "Swedish",
#     "Tamil",
#     "Telugu",
#     "Thai",
#     "Chinese (Taiwan)",
#     "Turkish",
#     "Urdu",
#     "Ukrainian",
#     "Vietnamese",
#     "Welsh"
# ]


if "native_lang_code" not in st.session_state.keys():
    st.session_state["native_lang_code"] = "ko"

# if "image_on" not in st.session_state.keys():
#     st.session_state["image_on"] = False

if "vocab_df" not in st.session_state.keys():
    vocab_df = load_data()
    st.session_state["vocab_df"] = vocab_df

if "lang_options" not in st.session_state.keys():
    translator = gct.GCTranslateUtils()
    st.session_state["lang_options"] = translator.get_supported_languages()

if "user_openai_api_key" in st.session_state and "native_lang" in st.session_state:
    os.environ["OPENAI_API_KEY"] = st.session_state["user_openai_api_key"]
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

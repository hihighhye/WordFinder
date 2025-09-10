import streamlit as st


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
 
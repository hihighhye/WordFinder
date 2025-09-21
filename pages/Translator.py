import streamlit as st
from crews.translator_crew import TranslatorCrew


@st.cache_resource()
def create_translator_crew():
    st.session_state["translator_crew"] = TranslatorCrew()
    print("Created new Translator Crew!")
    return st.session_state["translator_crew"]

st.set_page_config(
    page_title="Word Finder - Translator",
)

st.title("Sentence Translator")

native_lang = st.session_state["native_lang"]
translator_crew = create_translator_crew()

lang_mode = st.selectbox("Depart Language", (
    f"English to {native_lang}",
    f"{native_lang} to English"
))

depart_lang = "English"
destin_lang = native_lang

if lang_mode == f"{native_lang} to English":
    depart_lang = native_lang
    destin_lang = "English"

sentence = st.text_area("Phrases/Sentences", key="sentence_field")

if sentence:
    with st.spinner("Translating..."):
        res = translator_crew.translate(depart_lang, destin_lang, sentence)
        st.markdown(res)

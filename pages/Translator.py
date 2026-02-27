import streamlit as st
import gc_translate_utils as gct


def clear_sentence():
    st.session_state.sentence_field = ""

st.set_page_config(
    page_title="Word Finder - Translator",
)

st.title("Sentence Translator")


# translator_crew = st.session_state["translator_crew"] if "translator_crew" in st.session_state else None
translator = gct.GCTranslateUtils()
lang_idx = [lang.language_code for lang in translator.get_supported_languages()].index(st.session_state["native_lang_code"]) if "native_lang_code" in st.session_state else 0
native_lang = [lang.display_name for lang in translator.get_supported_languages()][lang_idx]

lang_mode = st.selectbox(
    "Depart Language", 
    (
        f"English to {native_lang}",
        f"{native_lang} to English"
    ),
    width=300,
    on_change=clear_sentence,
)

src_lang_code = "en"
tgt_lang_code = st.session_state["native_lang_code"]
if lang_mode == f"{native_lang} to English":
    src_lang_code = st.session_state["native_lang_code"]
    tgt_lang_code = "en"

sentence = st.text_area("Phrases/Sentences", key="sentence_field")

if sentence:
    if translator == None:
        st.error("Set your native language first to use translator.")
    else:
        with st.spinner("Translating..."):
            res = translator.translateText(sentence, src_lang_code=src_lang_code, tgt_lang_code=tgt_lang_code)
            st.markdown(res)

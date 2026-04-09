import streamlit as st
import gc_translate_utils as gct


def clear_sentence():
    st.session_state.sentence_field = None

st.set_page_config(
    page_title="Word Finder - Translator",
)

if "shuffled_vocab_table" in st.session_state:
    st.session_state.pop("shuffled_vocab_table")

st.title("Sentence Translator")


translator = gct.GCTranslateUtils()
lang_idx = [lang.language_code for lang in st.session_state["lang_options"]].index(st.session_state["native_lang_code"]) if "native_lang_code" in st.session_state else 0
native_lang = [lang.display_name for lang in st.session_state["lang_options"]][lang_idx]

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

import streamlit as st
import re
import pandas as pd
from crews.wordsfinder_crew import WordsFinderCrew


@st.dialog("You're missing some fields to fill")
def alert_missing_field():
    st.write("Please fill all essential blanks.")

@st.dialog("Unallowable characters has been used.")
def alert_unallowable_chars():
    st.write(r"Special characters are not allowed except for ' ', '\n' and '-' in Words/Phrases field.")

def check_validation(cat1, input_words):
    if not (cat1 and input_words):
        alert_missing_field()
        return False
    else:
        m = re.findall(r"[^A-Za-z\-\n ]", input_words)
        if m:
            alert_unallowable_chars()
            return False    
    return True

@st.cache_resource()
def create_wf_crew(native_lang):
    st.session_state["wordfinder_crew"] = WordsFinderCrew(native_lang=native_lang)
    return st.session_state["wordfinder_crew"]

def str_to_list(words):
    words = words.strip()
    words = re.sub(r'[ \t\r\f\v]{2,}', ' ', words)
    word_list = re.split(r'[,\n]+', words)
    word_list = [wd.strip() for wd in word_list]
    return word_list


st.set_page_config(
    page_title="Word Finder - Add New Words",
)

st.title("Add New Words")

st.markdown("""      
    You can add a number of words/phrases at once by joining each words/phrases with [enter ↵]. 
""")


wordsfinder_crew = create_wf_crew(st.session_state["native_lang"])

found_words = []
if "vocab_df" in st.session_state.keys():
    found_words = list(st.session_state["vocab_df"]["Word"])

with st.form("add_words", enter_to_submit=False, clear_on_submit=True):
    cat1 = st.text_input("*Category 1")
    cat2 = st.text_input("Category 2 (Optional)")

    input_words = st.text_area("*Words/Phrases")

    submitted = st.form_submit_button("Add")
    if submitted and check_validation(cat1, input_words):
        with st.spinner("Searching the words..."):
            if not cat2 or cat2.strip() == "":
                cat2 = "Etc."
            input_words = str_to_list(input_words)
            new_words = [w for w in input_words if w not in found_words]

            columns = ["Del", "Star", "Cat1", "Cat2", "Word", "Pronunciation", "Meaning", "Note", "Example"]
            result_df = pd.DataFrame(columns=columns)
            for word in new_words:
                try:
                    searched_word = wordsfinder_crew.search_words(word)
                    new_row = pd.DataFrame([
                        [
                            False, 
                            0, 
                            cat1, 
                            cat2, 
                            searched_word["word"], 
                            searched_word["pronunciation"], 
                            searched_word["meaning_eng"], 
                            searched_word["meaning_native"], 
                            ''
                        ]], columns=columns
                    )
                    result_df = pd.concat([result_df, new_row], axis=0)
                    st.toast(f"Now '{word}' is on the list.")
                except Exception:
                    new_row = pd.DataFrame([
                        [
                            False, 
                            0, 
                            cat1, 
                            cat2, 
                            word, 
                            "", 
                            "Cannot find the meaning of the word.", 
                            "", 
                            ""
                    ]], columns=columns
                    )
                    result_df = pd.concat([result_df, new_row], axis=0)
                    st.error(f"Something's wrong with '{word}'.")

            st.session_state["vocab_df"] = pd.concat([st.session_state["vocab_df"], result_df], axis=0).reset_index(drop=True)
            st.success("Now the words are available on my list.")
            st.rerun()
        
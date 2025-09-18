import streamlit as st
import re
import pandas as pd
from crews.wordsfinder_crew import WordsFinderCrew
import time


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
    print("Created new WF Crew!")
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
    found_words = [w.lower() for w in st.session_state["vocab_df"]["word"]]

placeholder = st.empty()
with placeholder.form("add_words_form", enter_to_submit=False, clear_on_submit=True):
    cat1 = st.text_input("*Category 1", key="cat1_field")
    cat2 = st.text_input("Category 2 (Optional)", key="cat2_field")

    input_words = st.text_area("*Words/Phrases", key="words_field")

    submitted = st.form_submit_button("Add")

if submitted and check_validation(cat1, input_words):
    placeholder.empty()  
    with st.spinner("Searching the meaning of words..."):
        if not cat2 or cat2.strip() == "":
            cat2 = "Etc."
        input_words = str_to_list(input_words)

        refined_words = []
        for word in input_words:
            refined_word = wordsfinder_crew.preprocess(word)
            refined_words.append(refined_word)

        new_words = [w for w in refined_words if w.lower() not in found_words]

        columns = ["del", "star", "cat1", "cat2", "word", "pronunciation", "meaning", "note", "example"]
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
                        ""
                    ]], columns=columns
                )
                result_df = pd.concat([result_df, new_row], axis=0)
                st.toast(f"'{word}' is added.")
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

        st.session_state["vocab_df"] = pd.concat([st.session_state["vocab_df"], result_df], axis=0).reset_index(drop=True)
    
    st.success("Now the words are available on My Vocabulary.")
    time.sleep(1)
    st.rerun()    
        
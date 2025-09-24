import streamlit as st
import re
import pandas as pd
import time
from datetime import date
import database_utils as db


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


wordsfinder_crew = st.session_state["wordfinder_crew"] if "wordfinder_crew" in st.session_state else None

found_words = []
if "vocab_df" in st.session_state.keys():
    found_words = [w.lower() for w in st.session_state["vocab_df"]["word"]]

image_on = st.session_state["image_on"] if "image_on" in st.session_state.keys() else False

today = date.today()
placeholder = st.empty()
with placeholder.form("add_words_form", enter_to_submit=True, clear_on_submit=True):
    cat1 = st.text_input("*Category 1", key="cat1_field")
    cat2 = st.text_input("Category 2 (Optional)", key="cat2_field")

    input_words = st.text_area("*Words/Phrases", key="words_field")

    submitted = st.form_submit_button("Add")

if submitted and check_validation(cat1, input_words):
    placeholder.empty()  
    with st.status("Searching the meaning of words...") as stat:
        if not cat2:
            cat2 = ""
        input_words = str_to_list(input_words)

        refined_words = []
        for word in input_words:
            refined_word = wordsfinder_crew.preprocess(word)
            refined_words.append(refined_word)

        new_words = [w for w in refined_words if w.lower() not in found_words]

        columns = ["cat1", "cat2", "word", "pronunciation", "meaning", "note", "example", "star", "img", "search_date"]
        new_records = []
        for word in new_words:
            try:
                stat.update(label=f"Searching the meaning of words...", state="running")
                searched_word = wordsfinder_crew.search_words(word)
                image = ""
                if image_on:
                    image = wordsfinder_crew.search_image(word)

                new_row = (
                        cat1, 
                        cat2, 
                        searched_word["word"], 
                        searched_word["pronunciation"], 
                        searched_word["meaning_eng"], 
                        searched_word["meaning_native"], 
                        "", # example
                        image,
                        today,
                )    
                new_records.append(new_row)
                st.toast(f"'{word}' is added.")
            except Exception:
                stat.update(label=f"Failed to find the meaning of {word}", state="error")
                new_row = (
                        cat1, 
                        cat2, 
                        word, 
                        "", 
                        "Cannot find the meaning of the word.", 
                        "", # note
                        "", # example
                        "", # image
                        today,
                )
                new_records.append(new_row)

        stat.update(label="Saving new words...", state="running")
        try:
            db.insert_data(new_records)
        except:
            st.error("Failed to save words. Try again.")
        current_data = db.get_data()

        vocab_df = pd.DataFrame(current_data, columns=columns)
        st.session_state["vocab_df"] = vocab_df

        stat.update(label="Successfully saved.", state="complete")
        time.sleep(1)
    
    st.success("Now the words are available on My Vocabulary.")
    time.sleep(1)
    st.rerun()    
        
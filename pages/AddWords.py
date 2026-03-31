import streamlit as st
import re
import pandas as pd
import time
from datetime import date
import database_utils as db
import gc_translate_utils as gct
import requests


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

if "shuffled_vocab_table" in st.session_state:
    st.session_state.pop("shuffled_vocab_table")

st.title("Add New Words")

st.markdown("""      
    You can add a number of words/phrases at once by joining each words/phrases with [enter ↵]. 
""")


found_words = []
if "vocab_df" in st.session_state.keys():
    found_words = [w.lower() for w in st.session_state["vocab_df"]["word"]]

wordnik_api_key = st.secrets["wordnik_api_key"]
pixabay_api_key = st.secrets["pixabay_api_key"]

translator = gct.GCTranslateUtils()

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

        refined_words = input_words
        # for word in input_words:
        #     refined_word = wordsfinder_crew.preprocess(word)
        #     refined_words.append(refined_word)

        new_words = [w for w in refined_words if w.lower() not in found_words]

        columns = ["cat1", "cat2", "word", "pronunciation", "meaning", "note", "example", "star", "synonym", "antonym", "img", "search_date"]
        new_records = []
        for word in new_words:
            meaning_native = translator.translateText(word)
            try:
                stat.update(label=f"Searching the meaning of words...", state="running")
                # res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
                res = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/definitions?limit=5&includeRelated=false&useCanonical=false&includeTags=false&api_key={wordnik_api_key}")
                searched_word = res.json()
                image = ""
                # if image_on:
                #     image = wordsfinder_crew.search_image(word)

                image_res = requests.get(f"https://pixabay.com/api/?key={pixabay_api_key}&q={word}&image_type=photo")
                try:
                    image = image_res.json()["hits"][0]["webformatURL"]
                    # print(image)
                except Exception as e:
                    print(e)

                meaning_eng = ""
                phonetic = ""
                synonyms = ""
                antonyms = ""

                ################################################################################
                # for meaning in searched_word["meanings"]:
                #     meaning_eng += meaning["partOfSpeech"] + ". "
                #     for defin in meaning["definitions"]:
                #         meaning_eng += defin["definition"] + " "
                #         if len(defin["synonyms"]) > 0:
                #             synonyms += ", ".join([s for s in defin["synonyms"]])
                #         if len(defin["antonyms"]) > 0:
                #             antonyms += ", ".join([s for s in defin["antonyms"]])
                ################################################################################

                try:
                    current_pos = ""
                    for w_obj in searched_word:
                        if "text" not in w_obj.keys():
                            continue
                        if "partOfSpeech" in w_obj.keys() and current_pos != w_obj["partOfSpeech"]:
                            current_pos = w_obj["partOfSpeech"]
                            meaning_eng += w_obj["partOfSpeech"] + ") " + w_obj["text"]
                        elif "partOfSpeech" in w_obj.keys():
                            meaning_eng += " // " + w_obj["text"]
                        else:
                            meaning_eng += " /// " + w_obj["text"]
                    meaning_eng = re.sub(r'<[^>]+>', '', meaning_eng)
                except:
                    print("[Error-json check] ", searched_word)

                res = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/pronunciations?useCanonical=false&limit=10&api_key={wordnik_api_key}")
                phonetics = res.json()

                for data in phonetics:
                    if "rawType" in data.keys() and data["rawType"] == "IPA":
                        phonetic = data["raw"]
                        break

                if not phonetic:
                    if "raw" in phonetics[0]:
                        phonetic = phonetics[0]["raw"]

                try:
                    res = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/relatedWords?useCanonical=false&relationshipTypes=synonym&limitPerRelationshipType=3&api_key={wordnik_api_key}")
                    synonyms = res.json()[0]["words"]
                    synonyms = ", ".join(synonyms)
                except:
                    pass
        
                try:
                    res = requests.get(f"https://api.wordnik.com/v4/word.json/{word}/relatedWords?useCanonical=false&relationshipTypes=antonym&limitPerRelationshipType=3&api_key={wordnik_api_key}")
                    antonyms = res.json()[0]["words"]
                    antonyms = ", ".join(antonyms)
                except:
                    pass

                new_row = (
                        cat1, 
                        cat2, 
                        searched_word[0]["word"], 
                        phonetic, # searched_word["phonetic"], 
                        meaning_eng, 
                        meaning_native, 
                        "", # example
                        synonyms,
                        antonyms,
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
                        meaning_native, # note
                        "", # example
                        "", # synonym
                        "", # antonym
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
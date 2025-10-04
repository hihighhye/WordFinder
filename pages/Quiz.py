import streamlit as st
from datetime import date, datetime
import pandas as pd
import time 


def select_cat1():
    cat1_list = vocab_df["cat1"].value_counts()
    cat1_options = ["Today"] + sorted(list(cat1_list.index))
    return st.selectbox(
        "Category 1", 
        options=cat1_options, 
        format_func=lambda option: option + f" ({len(today_words)})" if option == "Today" else option + f" ({cat1_list[option]})", 
        width=300,
    )

def select_cat2(selected_cat1):   
    vocab_table = vocab_df[vocab_df["cat1"]==selected_cat1].reset_index(drop=True)
    cat2_list = vocab_table["cat2"].value_counts()
    cat2_options = sorted(list(cat2_list.index))

    return st.selectbox(
        "Category 2", 
        options=cat2_options, 
        format_func=lambda option: option + f" ({cat2_list[option]})" if option in cat2_list.index else option, 
        width=300,
    )

st.set_page_config(
    page_title="Word Finder - Quiz",
)

st.title("Quiz")

vocab_df = st.session_state["vocab_df"]
vocab_df["cat2"] = vocab_df["cat2"].apply(lambda x: "Etc." if not x or x == "" else x)

today = datetime.strftime(date.today(), "%Y-%m-%d")
today_words = vocab_df[vocab_df["search_date"]==today].reset_index(drop=True)

table_columns = ["star", "word", "pronunciation", "meaning", "synonym", "antonym", "note", "example", "img"]
placeholder = st.empty()

if "shuffled_vocab_table" not in st.session_state.keys():
    with placeholder.container():
        st.markdown("""      
            Choose the range of words to review. 
        """)
        
        selected_cat1 = select_cat1()
        if selected_cat1 == "Today":
            vocab_table = today_words

        else:
            selected_cat2 = select_cat2(selected_cat1)
            vocab_table = vocab_df[(vocab_df["cat1"]==selected_cat1) & (vocab_df["cat2"]==selected_cat2)].reset_index(drop=True)
        
        vocab_table = vocab_table[table_columns]
        shuffled_vocab_table = vocab_table.sample(frac=1).reset_index(drop=True)

        start = st.button("Start", type="primary", width=200, disabled=(selected_cat1 is None))
        if start:
            st.session_state["shuffled_vocab_table"] = shuffled_vocab_table
            st.session_state["quiz_index"] = 0
            # placeholder.empty()
else:
    shuffled_vocab_table = st.session_state["shuffled_vocab_table"]
    cur_idx = st.session_state["quiz_index"]
    cur_row = shuffled_vocab_table.loc[cur_idx]
    total_len = len(shuffled_vocab_table)
    if "quiz_end" not in st.session_state.keys():
        st.session_state["quiz_end"] = False

    if st.session_state["quiz_end"]:
        st.subheader("You've reviewed all words!")
        st.balloons()
        time.sleep(2)
        st.session_state.pop("shuffled_vocab_table")
        st.session_state.pop("quiz_index")   
        st.session_state.pop("quiz_end") 
        st.rerun()

    else:
        placeholder_2 = st.empty()
        with placeholder_2.container():
            with st.container(height=400, width="stretch", gap="medium"):
                with st.container(horizontal=True, horizontal_alignment="right"):
                    st.badge(":material/star:" * cur_row["star"], color="orange")
                
                left, right = st.columns(2, gap="medium", vertical_alignment="center")
              
                left.title(cur_row["word"])
                left.text(cur_row['pronunciation'])
                
                try:
                    right.image(cur_row["img"])
                except:
                    pass
                
                help = st.toggle("help")
                if help:
                    with st.container(border=True, width="stretch", height=150):
                        st.markdown("""
                                    <style>
                                    .meaning {
                                        font-weight: bold;
                                    }
                                    .note {
                                        font-weight: 400;
                                    }
                                    </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""<div class='meaning'>Meaning: <div>
                                        <div class='meaning'>{cur_row['meaning']}</div><br>
                        """, unsafe_allow_html=True)

                        with st.container(border=False):
                            with st.container(border=False, horizontal=True):
                                st.badge("Synonym", icon=":material/check:", color="yellow")
                                st.markdown(f"{cur_row['synonym']}")
                            with st.container(border=False, horizontal=True):
                                st.badge("Antonym", icon=":material/check:", color="blue")
                                st.markdown(f"{cur_row['antonym']}")


            with st.container(horizontal=True, horizontal_alignment="center"):
                if st.button("Prev", disabled=(cur_idx==0)):
                    st.session_state["quiz_index"] -= 1
                    st.rerun()
                if st.button("Next"):
                    if cur_idx+1 < total_len:
                        st.session_state["quiz_index"] += 1
                    elif cur_idx+1 == total_len:
                        placeholder_2.empty()
                        st.session_state["quiz_end"] = True
                    st.rerun()

            with st.container(horizontal=True, horizontal_alignment="center"):
                st.text(f"{cur_idx+1} / {total_len}")

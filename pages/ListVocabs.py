import streamlit as st
import pandas as pd
import database_utils as db


@st.dialog(":material/delete: Delete Confirmation")
def confirm_del():
    st.write("Are you sure to delete selected words?")
    
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("Cancel", type="primary"):
            st.rerun()
        if st.button("Confirm", type="secondary"):
            delete_words()
            st.rerun()

def edit_data():
    vocab_df = st.session_state["vocab_df"]
    updated_rows = st.session_state["updated_rows"]
    edited_log = st.session_state["updated_log"]["edited_log"]
    
    for d_idx, content in updated_rows["edited_rows"].items():
        word = find_word(d_idx)
        w_idx = vocab_df[vocab_df["word"]==word].index[0]

        for column, val in content.items():
            vocab_df.loc[w_idx, column] = val

            if column != "del":
                if word not in edited_log.keys():
                    edited_log[word] = dict()
                edited_log[word][column] = val
                 
    st.session_state["vocab_df"] = vocab_df
    st.session_state["updated_log"]["edited_log"] = edited_log

def save_data():
    updated_log = st.session_state["updated_log"]

    for word, content in updated_log["edited_log"].items():
        set_clause = []
        for column, val in content.items():
            if type(val) == str:
                set_clause.append(f"{column}='{val}'") 
            else:
                set_clause.append(f"{column}={val}") 
        set_clause = ", ".join(set_clause)

        db.update_data(word, set_clause)

    del_words = updated_log["deleted_log"]
    del_words = list(map(lambda x: f"'{x}'", del_words))
    del_words = ", ".join(del_words)

    db.delete_data(del_words)

    st.toast("Saved!")
    st.session_state["updated_log"] = {"edited_log": dict(), "deleted_log": list()}

def delete_words():
    vocab_table = st.session_state["vocab_table"]
    vocab_df = st.session_state["vocab_df"]
    deleted_log = st.session_state["updated_log"]["deleted_log"]
    
    del_words = []
    del_words = list(vocab_table[vocab_table["del"]==True]["word"])
    deleted_log.extend(del_words)

    st.session_state["updated_log"]["deleted_log"] = deleted_log
    st.session_state["vocab_df"] = vocab_df[~vocab_df['word'].isin(del_words)].reset_index(drop=True)
    st.toast("Deleted!")
 
def find_word(d_idx):
    vocab_table = st.session_state["vocab_table"]
    return vocab_table.loc[d_idx, "word"]

st.set_page_config(
    page_title="Word Finder - My Vocabulary",
)

st.title("My Vocabulary")


vocab_df = st.session_state["vocab_df"]
if "updated_log" not in st.session_state.keys():
    st.session_state["updated_log"] = {"edited_log": dict(), "deleted_log": list()}

vocab_df["cat2"] = vocab_df["cat2"].apply(lambda x: "Etc." if not x or x == "" else x)

table_columns = ["del", "star", "word", "pronunciation", "meaning", "note", "example"]

cat1_list = vocab_df["cat1"].value_counts()
cat1_options = sorted(list(cat1_list.index))
selected_cat1 = st.pills("Category 1", options=cat1_options, format_func=lambda option: option + f" ({cat1_list[option]})", selection_mode="multi")

if selected_cat1:
    vocab_table = vocab_df[vocab_df["cat1"].isin(selected_cat1)].reset_index(drop=True)
    
    cat2_list = vocab_table["cat2"].value_counts()
    cat2_options = sorted(list(cat2_list.index))
    selected_cat2 = st.segmented_control("Category 2", options=cat2_options, format_func=lambda option: option + f" ({cat2_list[option]})", selection_mode="multi", width="stretch")

    if selected_cat2:
        vocab_table = vocab_table[vocab_table["cat2"].isin(selected_cat2)].reset_index(drop=True)
    
    vocab_table = vocab_table[table_columns]
    st.session_state["vocab_table"] = st.data_editor(
        vocab_table, 
        column_config={
            "star": st.column_config.NumberColumn(
                "star",
                help="How much is the word hard to memorize (1-5)?",
                min_value=1,
                max_value=5,
                step=1,
                format="%d ⭐",
            ),
            "word": st.column_config.TextColumn(
                disabled=True,
            ),
        },
        key="updated_rows",
        on_change=edit_data,
        width="stretch", 
        hide_index=True,
    )

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Delete"):
            confirm_del()

        if st.button("Save"):
            save_data()
            

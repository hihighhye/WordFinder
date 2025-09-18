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
    vocab_table = st.session_state["vocab_table"]
    vocab_df = st.session_state["vocab_df"]
    updated_rows = st.session_state["updated_rows"]
    
    for d_idx, content in updated_rows["edited_rows"].items():
        word = find_word(d_idx)
        w_idx = vocab_df[vocab_df["word"]==word].index[0]

        for column, val in content.items():
            vocab_table.loc[d_idx, column] = val
            if column == "del":
                continue
            vocab_df.loc[w_idx, column] = val
            
    st.session_state["vocab_df"] = vocab_df
    st.session_state["vocab_table"] = vocab_table

def save_data():
    vocab_table = st.session_state["vocab_table"]
    updated_rows = st.session_state["updated_rows"]
    
    for d_idx, content in updated_rows["edited_rows"].items():
        word = vocab_table.loc[d_idx, "word"]

        set_clause = ""
        for column, val in content.items():
            if column == "del":
                continue
            set_clause += f"{column}={val} "
        set_clause.strip()

        db.update_data(word, set_clause)

    st.toast("Saved!")

def delete_words():
    vocab_table = st.session_state["vocab_table"]
    updated_rows = st.session_state["updated_rows"]
    
    del_words = []
    for d_idx, content in updated_rows["edited_rows"].items():
        word = vocab_table.loc[d_idx, "word"]
   
        for column, val in content.items():
            if column == "del" and val == True:
                del_words.append(f"'{word}'")
                break
    
    del_words = ", ".join(del_words)

    db.delete_data(del_words)
    st.toast("Deleted!")

    vocab_df = db.get_data()

    st.session_state["vocab_df"] = pd.DataFrame(vocab_df, columns=[
        "cat1", "cat2", "word", "pronunciation", "meaning", 
        "note", "example", "star", "search_date"]
    )
    
def find_word(d_idx):
    vocab_table = st.session_state["vocab_table"]
    return vocab_table.loc[d_idx, "word"]

st.set_page_config(
    page_title="Word Finder - My Vocabulary",
)

st.title("My Vocabulary")


vocab_df = st.session_state["vocab_df"]

vocab_df["cat2"] = vocab_df["cat2"].apply(lambda x: "Etc." if not x or x == "" else x)
vocab_df["del"] = False

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
            

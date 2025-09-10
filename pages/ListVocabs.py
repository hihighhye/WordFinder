import streamlit as st
import pandas as pd
from googlesheets_utils import GooglesheetUtils


@st.cache_resource(show_spinner="Loading your vocab...")
def get_resource():
    googlesheet = GooglesheetUtils(spreadsheet_id="1hFNuCdmySJodQM5qsR5FJ6pkPLQc5DbXwP7h74pwTs8")

    values = googlesheet.get_data("Behave!B5:H")

    vocab_df = pd.DataFrame(values)
    vocab_df.columns = ["Cat1", "Cat2", "Word", "Pronunciation", "Meaning", "Note", "Example"]
    vocab_df["Cat2"] = vocab_df["Cat2"].apply(lambda x: "Etc" if not x or x == "" else x)
    vocab_df["Star"] = 0
    vocab_df["Del"] = False
    vocab_df = vocab_df.fillna("")
    return vocab_df

@st.dialog(":material/delete: Delete Confirmation")
def confirm_del():
    st.write("Are you sure to delete selected words?")
    
    with st.container(horizontal=True, horizontal_alignment="center"):
        if st.button("Cancel", type="primary"):
            st.rerun()
        if st.button("Confirm", type="secondary"):
            current_vocab_df = st.session_state["vocab_df"]
            st.session_state["vocab_df"] = current_vocab_df[current_vocab_df["Del"]==False].reset_index(drop=True)
            st.rerun()

def handle_data_change():
    vocab_df = st.session_state["vocab_df"]
    updated_rows = st.session_state["updated_rows"]
    
    for d_idx, content in updated_rows["edited_rows"].items():
        word = find_word(d_idx)
        w_idx = vocab_df[vocab_df["Word"]==word].index[0]

        for column, val in content.items():
            vocab_df.loc[w_idx, column] = val

    st.session_state["vocab_df"] = vocab_df

def find_word(d_idx):
    vocab_table = st.session_state["vocab_table"]
    return vocab_table.loc[d_idx, "Word"]

st.set_page_config(
    page_title="Word Finder - My Vocabulary",
)

st.title("My Vocabulary")


if "vocab_df" not in st.session_state.keys():
    st.session_state["vocab_df"] = get_resource()

vocab_df = st.session_state["vocab_df"]

table_columns = ["Del", "Star", "Word", "Pronunciation", "Meaning", "Note", "Example"]

cat1_list = vocab_df["Cat1"].value_counts()
cat1_options = sorted(list(cat1_list.index))
selected_cat1 = st.pills("Category 1", options=cat1_options, format_func=lambda option: option + f" ({cat1_list[option]})", selection_mode="multi")

if selected_cat1:
    vocab_table = vocab_df[vocab_df["Cat1"].isin(selected_cat1)].reset_index(drop=True)
    
    cat2_list = vocab_table["Cat2"].value_counts()
    cat2_options = sorted(list(cat2_list.index))
    selected_cat2 = st.segmented_control("Category 2", options=cat2_options, format_func=lambda option: option + f" ({cat2_list[option]})", selection_mode="multi", width="stretch")

    if selected_cat2:
        vocab_table = vocab_table[vocab_table["Cat2"].isin(selected_cat2)].reset_index(drop=True)
    
    vocab_table = vocab_table[table_columns]
    st.session_state["vocab_table"] = st.data_editor(
        vocab_table, 
        column_config={
            "Star": st.column_config.NumberColumn(
                "Star",
                help="How much is the word hard to memorize (1-5)?",
                min_value=1,
                max_value=5,
                step=1,
                format="%d ⭐",
            ),
            "Word": st.column_config.TextColumn(
                disabled=True,
            )
        },
        key="updated_rows",
        on_change=handle_data_change,
        width="stretch", 
        hide_index=True,
    )

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Delete"):
            confirm_del()

        if st.button("Save"):
            pass

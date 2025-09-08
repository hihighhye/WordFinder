import streamlit as st
import pandas as pd
from googlesheets_utils import GooglesheetUtils


@st.cache_resource(show_spinner="Loading your vocab...")
def get_resource():
    googlesheet = GooglesheetUtils(spreadsheet_id='1hFNuCdmySJodQM5qsR5FJ6pkPLQc5DbXwP7h74pwTs8')

    values = googlesheet.get_columns('Behave!B5:H439')

    vocab_df = pd.DataFrame(values)
    vocab_df.columns = ['Cat1', 'Cat2', 'Word', 'Pronunciation', 'Meaning', 'Note', 'Example']
    vocab_df['Cat2'] = vocab_df['Cat2'].apply(lambda x: "Etc" if x == "" else x)
    vocab_df['Star'] = 0
    return vocab_df

st.set_page_config(
    page_title="My Vocabulary",
    page_icon="📒"
)

st.title("My Vocabulary")

with st.sidebar:
    file = st.file_uploader("Upload a .csv or .xlsx file.", 
                            type=["csv", "xlsx"]
    )

vocab_df = get_resource()
table_columns = ['Star', 'Word', 'Pronunciation', 'Meaning', 'Note', 'Example']

cat1_list = vocab_df['Cat1'].value_counts()
cat1_options = sorted(list(cat1_list.index))
selected_cat1 = st.pills("Category 1", options=cat1_options, format_func=lambda option: option + f' ({cat1_list[option]})', selection_mode="multi")

if selected_cat1:
    vocab_table = vocab_df[vocab_df['Cat1'].isin(selected_cat1)].reset_index(drop=True)
    
    cat2_list = vocab_table['Cat2'].value_counts()
    cat2_options = sorted(list(cat2_list.index))
    selected_cat2 = st.segmented_control("Category 2", options=cat2_options, format_func=lambda option: option + f' ({cat2_list[option]})', selection_mode="multi", width="stretch")

    if selected_cat2:
        vocab_table = vocab_table[vocab_table['Cat2'].isin(selected_cat2)].reset_index(drop=True)
    
    vocab_table = vocab_table[table_columns]
    edited_df = st.data_editor(
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
        },
        width="stretch", 
    )
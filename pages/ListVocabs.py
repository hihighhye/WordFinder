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
    initialize_session_log()

def delete_words():
    vocab_table = st.session_state["vocab_table"]
    vocab_df = st.session_state["vocab_df"]
    deleted_log = st.session_state["updated_log"]["deleted_log"]
    
    del_words = []
    del_words = list(vocab_table[vocab_table["del"]==True]["word"])
    deleted_log.extend(del_words)

    st.session_state["updated_log"]["deleted_log"] = deleted_log
    st.session_state["vocab_df"] = vocab_df[~vocab_df["word"].isin(del_words)].reset_index(drop=True)
    st.session_state["vocab_table"] = vocab_table[vocab_table["del"]==False].reset_index(drop=True)
    st.toast("Press [Save] button to save deleted result.")
 
def find_word(d_idx):
    vocab_table = st.session_state["vocab_table"]
    return vocab_table.loc[d_idx, "word"]

def initialize_session_log():
    st.session_state["updated_log"] = {"edited_log": dict(), "deleted_log": list()}

@st.cache_data()
def export_data(df):
    return df.to_csv().encode("utf-8")

def change_edit_mode(val):
    st.session_state["edit_mode"] = val
    st.session_state["vocab_copy"] = vocab_df.copy()

def set_background_color(_):
    return "font-weight: bold;"

def generate_example(word):
    return wordfinder_crew.generate_example(word)
    

st.set_page_config(
    page_title="Word Finder - My Vocabulary",
)

st.title("My Vocabulary")

if "updated_log" not in st.session_state.keys():
    initialize_session_log()

if "edit_mode" not in st.session_state.keys():
    st.session_state["edit_mode"] = False

vocab_df = st.session_state["vocab_df"]
vocab_df["cat2"] = vocab_df["cat2"].apply(lambda x: "Etc." if not x or x == "" else x)

wordfinder_crew = st.session_state["wordfinder_crew"] if "wordfinder_crew" in st.session_state else None

table_columns = ["star", "word", "pronunciation", "meaning", "note", "example"]

cat1_list = vocab_df["cat1"].value_counts()
cat1_options = sorted(list(cat1_list.index))

try:
    selected_cat1 = st.pills(
        "Category 1", 
        options=cat1_options, 
        format_func=lambda option: option + f" ({cat1_list[option]})", 
        selection_mode="multi",
        default=st.session_state["list_cat1"] if "list_cat1" in st.session_state else None,
    )
except:
    st.session_state.pop("list_cat1")
    save_data()
    change_edit_mode(False)
    st.rerun()

if selected_cat1:
    st.session_state["list_cat1"] = selected_cat1
    st.session_state.pop("list_cat2", None)
    vocab_table = vocab_df[vocab_df["cat1"].isin(selected_cat1)].reset_index(drop=True)
    
    cat2_list = vocab_table["cat2"].value_counts()
    cat2_options = sorted(list(cat2_list.index))

    try:
        selected_cat2 = st.pills(
            "Category 2", 
            options=cat2_options, 
            format_func=lambda option: option + f" ({cat2_list[option]})", 
            selection_mode="multi",
            default=st.session_state["list_cat2"] if "list_cat2" in st.session_state else None,
        )
    except:
        st.session_state.pop("list_cat2")
        save_data()
        change_edit_mode(False)
        st.rerun()

    if selected_cat2:
        st.session_state["list_cat2"] = selected_cat2
        vocab_table = vocab_table[vocab_table["cat2"].isin(selected_cat2)].reset_index(drop=True)
    
    vocab_table = vocab_table[table_columns]

    if not st.session_state["edit_mode"]:
        download_file = export_data(vocab_table)
        with st.container(horizontal=True, horizontal_alignment="right"):
            edit = st.button("Edit", on_click=change_edit_mode, args=(True,))
            st.download_button(
                "Download",
                data=download_file,
                file_name=f"{'-'.join(selected_cat1)}_partial.csv" if selected_cat2 else f"{'-'.join(selected_cat1)}_all.csv",
                mime="text/csv",
                icon=":material/download:"
            )

        styled_vocab_table = vocab_table.style.map(set_background_color, subset=["word"])
        event = st.dataframe(
            styled_vocab_table, 
            column_config={
                "star": st.column_config.NumberColumn(
                    "star",
                    help="How much is the word hard to memorize(0-5)?",
                    format="%d ⭐",
                ),
            },
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        
        if len(event.selection["rows"]):
            if wordfinder_crew == None:
                st.error("Set your OpenAI API key to generate examples.")
            else:
                row_idx = event.selection["rows"][0]
                word = vocab_table.loc[row_idx, "word"]
                if st.button("generate example", type="primary"):
                    with st.spinner("Generating an example..."):
                        example = generate_example(word)
                        st.write(example)

    else:
        # placeholder.empty()
        vocab_table["del"] = False
        vocab_table = vocab_table[["del"] + table_columns]
        st.session_state["vocab_table"] = st.data_editor(
            vocab_table, 
            column_config={
                "star": st.column_config.NumberColumn(
                    "star",
                    help="How much is the word hard to memorize(0-5)?",
                    min_value=0,
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

            with st.container(horizontal=True, horizontal_alignment="right"):
                if st.button("Cancel"):
                    st.session_state["vocab_df"] = st.session_state["vocab_copy"]
                    initialize_session_log()
                    st.toast("Canceled.")
                    change_edit_mode(False)
                    st.rerun()

                if st.button("Save", type="primary"):
                    save_data()
                    change_edit_mode(False)
                    st.rerun()
                    

import streamlit as st
import re


@st.dialog("You're missing some fields to fill")
def alert_missing_field():
    st.write("Please fill all essential blanks.")

@st.dialog("Unallowable characters has been used.")
def alert_validation():
    st.write(r"Special characters are not allowed except for ' ', '\n' and '-' in Words/Phrases field.")


st.set_page_config(
    page_title="Add New Words",
    page_icon="🔍"
)

st.title("Add New Words")

st.markdown("""      
    You can add a number of words/phrases at once by joining each words/phrases with [enter ↵]. 
""")

with st.form("add_words", enter_to_submit=False):
    category_1 = st.text_input("*Category 1")
    category_2 = st.text_input("Category 2 (Optional)")

    words = st.text_area("*Words/Phrases")

    submitted = st.form_submit_button("Add")
    if submitted:
        if not (category_1 and words):
            alert_missing_field()
        else:
            m = re.findall(r'[^A-Za-z\-\n ]', words)
            if m:
                alert_validation()
            else:
                st.write("done")
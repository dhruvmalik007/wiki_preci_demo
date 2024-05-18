import streamlit as st


st.set_page_config(page_title="demo of demonstrating the agents for analyzing the wikipedia contribution data")



with st.form(key="agent description", border=True) as form_agent:
    text_input = st.text_area("add the user query regarding the wikipedia contribution")
    st.form_submit_button(label="Submit query")
    
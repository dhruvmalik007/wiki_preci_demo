import streamlit as st
from wikipediaapi import Wikipedia
from textblob import TextBlob
import requests
import sys
sys.path.append('.')
from src.utils.reverts import Reverts
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Wiki preci", page_icon="✌️", layout="wide")

st.session_state['search'] = ''

def select_topic(revertObj: Reverts):
    value = st_searchbox(revertObj.stream_result,key="wiki_searchbox")  
    st.session_state['search'] = value 
    st.info("Topic selected: {}".format(st.session_state['search']))
    
def main():
    revertObj: Reverts
    st.title("Wiki precis project")
     ## ("en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh") dropdown list
    select_country = st.selectbox("Select your country", options=("en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh") )
    revertObj = Reverts(select_country)
    st.info("API endpoint created: {}".format(revertObj.base_url))
    select_topic(revertObj)
    submit = st.button("Submit")
    if submit:
        page_title = st.session_state['search']
        st.info("the following topic has the reverts:" + str(revertObj.count_revisions(page_title=page_title)))
if __name__ == "__main__":
   main()
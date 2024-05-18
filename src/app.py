import streamlit as st
from wikipediaapi import Wikipedia
from textblob import TextBlob
import requests
import sys
sys.path.append('.')
from src.utils.reverts import Reverts, CloudFunctions
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Wiki preci", page_icon="✌️", layout="wide")

st.session_state['search'] = ''

def select_topic(revertObj: Reverts):
    value = st_searchbox(revertObj.stream_result,key="wiki_searchbox")  
    st.session_state['search'] = str(value) 
    st.info("Topic selected: {}".format(st.session_state['search']))
    return value

def showcase_reverts_statistics(revert_obj: Reverts, container):
    page_title = st.session_state['search']
    try:
        container.info("revisions amount" + str(revert_obj.count_revisions(page_title)))
        container.info("the latest revision date: " + str(revert_obj.get_latest_revision_date(article_title=page_title)))
    except Exception as e:
        print(e)

def showcase_pagehistory_migration(cloud_fns: CloudFunctions, container):
    page_title = st.session_state['search']
    cloud_fns.store_revisions_in_datastore(page_title)
    container.info("the migration of data is completed")
    # except Exception as e:
    #     print("in pagehistory_migration: " + str(e))    



def main():
    revertObj: Reverts
    cloud_fns: CloudFunctions
    st.title("Wiki precis project")
     ## ("en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh") dropdown list
    select_country = st.selectbox("Select your country", options=("en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh") )
    revertObj = Reverts(select_country)
    cloud_fns = CloudFunctions(select_country)
    st.info("API endpoint created: {}".format(revertObj.base_url))
    select_topic(revertObj)
    submit = st.button("get statistics")
    migrate_data = st.button("migrate wikipedia data.")
    container = st.container(height=500, border=True) 

    if submit:
        showcase_reverts_statistics(revert_obj=revertObj, container=container)
    if migrate_data:
        showcase_pagehistory_migration(cloud_fns=cloud_fns,container=container)
    

if __name__ == "__main__":
   main()
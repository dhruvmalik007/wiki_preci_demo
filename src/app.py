from streamlit_searchbox import st_searchbox
import sys
import requests
from textblob import TextBlob
from wikipediaapi import Wikipedia
import streamlit as st
import os
sys.path.append('.')
from src.utils.reverts import Reverts, CloudFunctions


st.set_page_config(page_title="Wiki preci", page_icon="✌️", layout="wide")

st.session_state['search'] = ''


def select_topic(revertObj: Reverts):
    value = st_searchbox(revertObj.stream_result, key="wiki_searchbox")
    if value:
        st.session_state['search'] = str(value)
    st.write("Topic selected: {}".format(revertObj.get_page_name(st.session_state['search'])))
    return value


def showcase_reverts_statistics(revert_obj: Reverts):
    page_title = st.session_state['search']
    try:
        st.info("revisions amount" +
                       str(revert_obj.count_revisions(page_title)))
        st.info("the latest revision date: " +
                       str(revert_obj.get_latest_revision_date(article_title=page_title)))

        revert_obj.get_revision_history(page_title)
    except Exception as e:
        print(e)


def showcase_pagehistory_migration(revert_obj: Reverts, num_of_records):
    page_title = st.session_state['search']
    # cloud_fns.store_revisions_in_datastore(page_title)
    st.dataframe(revert_obj.get_revisions_with_tags_and_reverts(
    page_title=page_title,
    showcase_records= num_of_records
    
    ))
    revert_obj.store_results(page_title)
    st.info("the migration of data is completed")
    # except Exception as e:
    #     print("in pagehistory_migration: " + str(e))



def main():
    revertObj: Reverts
    cloud_fns: CloudFunctions
    st.title("Wiki precis project")
    # ("en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh") dropdown list
    select_country = st.selectbox("Select your country", options=(
        "en", "he", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh"))
    
    revert_records = st.text_input("number of revert records you want to see",)
    revertObj = Reverts(select_country)
    cloud_fns = CloudFunctions(select_country)
    st.info("API endpoint created: {}".format(revertObj.base_url))
    select_topic(revertObj)
    submit = st.button("get statistics")
    revert_data = st.button("migrate wikipedia data.")
    if submit:
        showcase_reverts_statistics(revert_obj=revertObj)
    if revert_data:
        showcase_pagehistory_migration(revert_obj=revertObj, num_of_records= int(revert_records))

if __name__ == "__main__":
    main()

import streamlit as st
from wikipediaapi import Wikipedia
from textblob import TextBlob
import requests

### Credits to Yakir fenton for the contribution of functions for getting revision parameters and reverts.

def get_revisions_with_tags_and_reverts(page_title):
    revisions_with_tags_reverts = []
    continue_flag = True
    continue_params = ''
    total_revisions = 0
    # revisions_count = 0
    last_revision_content = None
    while continue_flag:
        # Construct API URL
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={page_title}&rvlimit=max&rvprop=tags|user|content&format=json{continue_params}"
        # Make API request
        response = requests.get(api_url)
        if response.status_code != 200:
            print("Failed to fetch revisions.")
            return None

        # Parse JSON response
        data = response.json()
        # Extract revisions and their tags
        page_id = list(data["query"]["pages"].keys())[0]
        revisions = data["query"]["pages"][page_id]["revisions"]
        total_revisions += len(revisions)
        # revisions_count += len(data["query"]["pages"][page_id]["revisions"])
        for revision in revisions:
            # print(revision)
            # break
            try:
              revision_info = {"user": revision["user"], "content": revision["*"]}
            except:
              st.error(revision)
              break
            # print(revision_info)
            if "tags" in revision:
                revision_info["tags"] = revision["tags"]
            else:
                revision_info["tags"] = []



            # Check if the revision is a revert
            if last_revision_content and is_revert(revision["*"], last_revision_content):
                revision_info["is_revert"] = True
            else:
                revision_info["is_revert"] = False

            revisions_with_tags_reverts.append(revision_info)
            last_revision_content = revision["*"]

        # Check if there are more revisions to fetch
        if 'continue' in data:
            continue_params = '&rvcontinue=' + data['continue']['rvcontinue']
        else:
            continue_flag = False
    
    st.info(f"Fetched {len(revisions)} revisions so far")
    st.write(revisions_with_tags_reverts)
    return revisions_with_tags_reverts


def is_revert(current_content, previous_content):
    # Check if the current content is identical to the previous content
    if current_content == previous_content:
        return True

    # Check if the current content contains certain keywords indicating a revert
    revert_keywords = ["revert", "rv", "undo", "rvv", "reverted", "revision"]
    for keyword in revert_keywords:
        if keyword in current_content.lower():
            return True

    return False

def count_revisions(page_title):
    revisions_count = 0
    continue_flag = True
    continue_params = ''

    while continue_flag:
        # Construct API URL
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={page_title}&rvslots=*&rvlimit=max&format=json{continue_params}"

        # Make API request
        response = requests.get(api_url)
        if response.status_code != 200:
            print("Failed to fetch revisions.")
            return None

        # Parse JSON response
        data = response.json()

        # Extract number of revisions
        page_id = list(data["query"]["pages"].keys())[0]
        revisions_count += len(data["query"]["pages"][page_id]["revisions"])
        # print(data["query"]["pages"][page_id]["revisions"])
        # Check if there are more revisions to fetch
        if 'continue' in data:
            continue_params = '&rvcontinue=' + data['continue']['rvcontinue']
        else:
            continue_flag = False

    return revisions_count



def main():
    st.title("Wiki precis project")
    st.form(key="details")
    value = st.text_input("Enter the name of the topic")
    submit = st.button("Submit")
    if submit:
        get_revisions_with_tags_and_reverts(value)

if __name__ == "__main__":
   main()
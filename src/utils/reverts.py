import requests
import streamlit as st
import requests
from typing import List
import pandas as pd
class Reverts():
    
    base_url: str
    def __init__(self,country_code):    
        self.base_url = f"https://{country_code}.wikipedia.org/w/api.php"
    
    def get_revisions_with_tags_and_reverts(self, page_title):
        """
        Fetches revisions for a page, including tags, user names, content, and revert information,
        presented in a clean tabular format.

        Args:
            page_title (str): The title of the Wikipedia page.

        Returns:
            list: A list of dictionaries containing revision details.
        """

        revisions = []
        continue_flag = True
        continue_params = ''
        last_revision_content = None

        while continue_flag:
            # Construct API URL
            api_url = self.base_url + ("action=query&prop=revisions&titles=" + page_title +
                                        "&rvlimit=max&rvprop=tags|user|content&format=json" + continue_params)
            # Make API request
            response = requests.get(api_url)
            if response.status_code != 200:
                print("Failed to fetch revisions.")
                return None

            # Parse JSON response
            data = response.json()
            page_id = list(data["query"]["pages"].keys())[0]

            # Extract revisions, handling potential missing revisions
            revisions_data = data["query"]["pages"][page_id].get("revisions", [])
            for revision in revisions_data:
                try:
                    revision_info = {
                        "user": revision["user"],
                        "content": revision["*"],
                        "tags": revision.get("tags", []),  # Handle missing tags
                        "is_revert": self.is_revert(revision["*"], last_revision_content)
                    }
                except Exception as e:  # Catch any exceptions during extraction
                    print(f"Error processing revision: {e}")
                    continue  # Skip problematic revisions and continue processing

                revisions.append(revision_info)
                last_revision_content = revision["*"]

            # Check if there are more revisions to fetch
            if 'continue' in data:
                continue_params = '&rvcontinue=' + data['continue']['rvcontinue']
            else:
                continue_flag = False

        # Return revisions as a pandas DataFrame for cleaner tabular display
        return pd.DataFrame(revisions)



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

    def count_revisions(self,page_title) -> int:
        revisions_count = 0
        continue_flag = True
        continue_params = ''

        while continue_flag:
            # Construct API URL
            api_url = self.base_url  + "?action=query&prop=revisions&titles=" + page_title + "&rvslots=*&rvlimit=max&format=json" + continue_params
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

    def get_page_name(self,search_term):
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_term,
            "srlimit": 1,  # Limit to top result
            "format": "json",
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            page_name = data['query']['allpages'][0]['title']
        except Exception as e:
            print(e)
            page_name = None
        return page_name
    def stream_result(self,search_term:str) -> List[any]:
        """
        gets the potential page name from the search term and streams the top 10 results 
        (can be modified to stream top N results).
        """
        params = {
        "action": "opensearch",
        "search": search_term,
        "limit": 10,  # Limit to 10 suggestions
        "format": "json",
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        return data[1] if data else []


    def get_revision_history(self,page_name):
        """
        Retrieves the revision history of the specified page, including user names, timestamps,
        and the first 10 revisions (or less if fewer exist).

        Args:
            page_name (str): The name of the Wikipedia page.

        Returns:
            pandas.DataFrame: A DataFrame containing revision metadata, capped at 10 rows.
        """

        params = {
            "action": "query",
            "prop": "revisions",
            "titles": page_name,
            "rvprop": "user|timestamp|comment",  # Include user, timestamp, and comment
            "rvlimit": 10,  # Limit to 10 revisions
            "format": "json",
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        revisions = []
        if page_name in data["query"]["pages"]:
            page_id = list(data["query"]["pages"].keys())[0]
            revisions = data["query"]["pages"][page_id]["revisions"]

        revision_data = []
        for revision in revisions:
            ## handling in case of the missing comments for the revision
            revision_data.append({
                "User": revision["user"],
                "Timestamp": revision["timestamp"],
                "Comment": revision.get("comment", ""),  
            })

        return st.pd.DataFrame(revision_data)[:10] 






import requests
import streamlit as st
import requests
from typing import List
import pandas as pd
from google.cloud.firestore_admin_v1 import FirestoreAdminClient
from google.cloud import datastore
import datetime
from dataclasses import dataclass
from google.cloud.datastore.client import Client
from dotenv import load_dotenv
import os
load_dotenv()

project_id = os.getenv("PROJECT_ID")



@dataclass
class Revision:
    user: str    
    content: str    
    tags: list[str]    
    is_revert: bool

@dataclass
class WikipediaPage:
    title: str
    revisions: list[Revision]







class Reverts():
    base_url: str
    datastore_client: datastore.Client
    def __init__(self,country_code):    
        self.base_url = f"https://{country_code}.wikipedia.org/w/api.php"
       # self.datastore = datastore.Client()
        
    
    def create_task(self):
        self.client = self.datastore.tran
        
    
    def get_revisions_with_tags_and_reverts(self, page_title):
        """
        Fetches revisions for a page, including tags, user names, content, and revert information,
        presented in a clean tabular format.

        Args:
            page_title (str): The title of the Wikipedia page.

        Returns:
            list: A list of dictionaries containing revision details.
        """
        revisions_with_tags_reverts = []
        continue_flag = True
        continue_params = ''
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
            # revisions_count += len(data["query"]["pages"][page_id]["revisions"])
            for revision in revisions:
                # print(revision)
                # break
                revision_info = {}
                if "user" in revision:
                    revision_info["user"] = revision["user"]
                else:
                    revision_info["user"] = []
                if "*" in revision:
                    revision_info["content"] = revision["*"]
                else:
                    revision_info["content"] = []
                if "tags" in revision:
                    revision_info["tags"] = revision["tags"]
                else:
                    revision_info["tags"] = []

                # Check if the revision is a revert
                if last_revision_content and self.is_revert(revision_info["content"], last_revision_content):
                    revision_info["is_revert"] = True
                    # print(revision_info["content"])
                else:
                    revision_info["is_revert"] = False

                revisions_with_tags_reverts.append(revision_info)
                last_revision_content = revision_info["content"]

            # Check if there are more revisions to fetch
            if 'continue' in data:
                continue_params = '&rvcontinue=' + data['continue']['rvcontinue']
            else:
                continue_flag = False
        # Return revisions as a pandas DataFrame for cleaner tabular display
        return WikipediaPage(
                    title=page_title,
        revisions=[Revision(**revision_info) for revision_info in revisions_with_tags_reverts]
        )



    def is_revert(self,current_content, previous_content) -> bool:
        # Check if the current content is identical to the previous content
        try:
            if current_content == previous_content:
                return True

            if isinstance(current_content, list):
                current_content = ' '.join(current_content)  
            
            # Check if the current content contains certain keywords indicating a revert
            revert_keywords = ["revert", "rv", "undo", "rvv", "reverted", "revision"]
            for keyword in revert_keywords:
                if keyword in current_content.lower():
                    return True
        except Exception as e:
            print("in is_revert fn:" + str(e))
        
        return False

    def count_revisions(self,topic):
        revisions_count = 0
        continue_flag = True
        continue_params = ''

        while continue_flag:
            # Construct API URL
            api_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={topic}&rvslots=*&rvlimit=max&format=json{continue_params}"

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
            "titles": "API|Main Page",
            "rvprop": "timestamp|user|comment|content",
            "rvslots": "main",
            "formatversion": "2",
            "format": "json"

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


#api.php?action=query&prop=revisions&titles=API:Geosearch&rvlimit=5&rvslots=main&rvprop=timestamp|user|comment&rvdir=newer&rvstart=2018-07-01T00:00:00Z&

    def get_latest_revision_date(self, article_title):
        """
        getting the newest revision date of the given article
        
        """
        
        params = {
        "action": "query",
        "format": "json",
        "titles": article_title,
        "prop": "revisions",
        "rvlimit": 1,
        "rvslots": "main",
        "rvprop": "timestamp",
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            print("Failed to fetch data.")
            return None

        # Parse the JSON response
        data = response.json()

        # Navigate through the nested JSON to find the revision data
        page_data = data.get('query', {}).get('pages', {})
        page_id = list(page_data.keys())[0]
        revisions = page_data[page_id].get('revisions', [])

        # Check if revisions are available
        if not revisions:
            return None

        # Extract the timestamp from the latest revision
        newest_revision_timestamp = revisions[0].get('timestamp', '')

        # Convert the timestamp string to a Unix timestamp
        newest_revision_date = datetime.datetime.strptime(newest_revision_timestamp, "%Y-%m-%dT%H:%M:%SZ").timestamp()

        return newest_revision_date

        
class CloudFunctions():
    datastore_client: Client
    revertObj: Reverts 

    def __init__(self, region) -> None:
        self.datastore_client = Client(project=project_id)
        self.revertObj= Reverts(region)
    
    
    def store_revisions_in_datastore(self, page_title):
        """
        stores uptodate revision history and other information of the wikipedia page.
        its use to initialise the storage of the given wikipedia page and subsequentially use the 
        update functions

        :page_title: for the specific page from which you need to fetch the parameters
        """
        st.info("doing the project with id:" + project_id)

        pageHistory = self.revertObj.get_revisions_with_tags_and_reverts(
            page_title)
        
        page_key = self.datastore_client.key('WikipediaPageHistory', pageHistory.title)

        st.info("page_key created as" + str(page_key))

        # now fetching the revision history into the datastore noSQL format.
        try:
            revision_data = [
                datastore.Entity(
                    key=page_key,
                    **{
                        'user': revision.user,
                        'content': revision.content,
                        'tags': revision.tags,
                        'is_revert': revision.is_revert,
                    }
                )
                for i, revision in enumerate(pageHistory.revisions)]
            
        
            # Save the page key and revision entities in a transaction
            with self.datastore_client.transaction() as txn:
                txn.put(page_key, {'title': pageHistory.title})
                txn.put(revision_data)
        except Exception as e:
            print("inside cloudfunctions.store_revisions_in_datastore: " + str(e))        
        



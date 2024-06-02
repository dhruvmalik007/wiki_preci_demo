##1/vizualization/mapping of the different contributions of each administrator
## 2/identification of administrators who try up the control of all wiki controversial pages related to israel/hamas /palestine...

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage


from typing import Tuple, Dict, List
from dotenv import load_dotenv
import os
import getpass






def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")

MODEL_SELECTION = ["gpt-3.5-turbo", "gpt-4o"]



class TopoiAgent():
    """
    It tries to implement the basic version of the topoi rational concept  that 
    tries to do the analysis between the different agents in order to get more comprehensive examples
    """
    
    def __init__(self, topic):
        self.tavilyObj = TavilySearchResults()
        self.query = topic
        
        _set_if_undefined("OPENAI_API_KEY")
        _set_if_undefined("LANGCHAIN_API_KEY")
        _set_if_undefined("TAVILY_API_KEY")
        
    
    
    

        
"""
These allow to create group of agents that work on the stragegies (reflection, ReACT or graph collaboration)
in order to generate the more optimum details regarding the nature 
of why there has been reverts, along with summarizing the reasons behind it.


"""
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Tuple, Dict, List
MODEL_SELECTION = ["gpt-3.5-turbo", "gpt-4o"]

REVERTS_EXPLANATION_PROMPT = """
You are a Large Language Model (LLM) within a multi-agent system specialized as the psychologist and can understand the nature of the revert messages for wikipedia 'TOPIC'.
Your primarily task is to analyse the various revert messages that are generated by the admin for every changes done by the USER in the 'TOPIC' . 
You have to read all of these revert messages and do the following 

- remember the relation between the writer of the changes with the admin of the wikipedia topic
- the user's query should only be addresses in case if they are asking regarding the nautre of the revert topic and reason
- also you need to generate the tags corresponding to each of the revert messages and then generate the statistics comparing revert messages and non-revert messages
- If user asks something that is not related to the TOPIC at all, then halt the processing and generate ERROR.
- TODO: Also use your memory for the reference (ToT, CoT)

Following is the nature of the prompt 



USER_PROMPT:
```
{user_prompt} for {topic}
```

ADDITIONAL_INFORMATION:
```
{additional_information}
```

OUTPUT_FORMAT:
* Your output response must be only a single JSON object to be parsed by Python's "json.loads()".
* The JSON must contain five fields: "reason", "positive", "negative", "confidence", and "info_utility".
   - "decision": The decision you made. Either `y` (for `Yes`) or `n` (for `No`).
   - "p_yes": Probability that the admin has reverted the changes because of the geunine reason. Ranging from 0 (lowest probability) to 1 (maximum probability).
   - "p_no": Probability that the  admin has reverted due to the biasnes by the admin and the change was correct. Ranging from 0 (lowest probability) to 1 (maximum probability).
   - "confidence": Indicating the confidence in the estimated probabilities you provided ranging from 0 (lowest confidence) to 1 (maximum confidence). Confidence can be calculated based on the quality and quantity of data used for the estimation.
   - "info_utility": Utility of the information provided in "ADDITIONAL_INFORMATION" to help you make the probability estimation ranging from 0 (lowest utility) to 1 (maximum utility).
* The sum of "p_yes" and "p_no" must equal 1.
* Output only the JSON object in your response. Do not include any other contents in your response.
"""




class ResearchAgent():
    agentLLM: ChatOpenAI
    tavily_research: TavilySearchResults
    revert_messages: Dict[str, List[Tuple[str,str]]] ## stores the tupple with admin name --> (sender and corresponding message)
    
    
    
     
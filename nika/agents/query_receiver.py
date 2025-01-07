from llm import OpenAI_LLM
from .prompts import query_receiver
import json
"""
Receives the user query 
Determin the relevance for data analysis as relevant/non-relevant
additional info is asked if the user query is not relevant

{
    "question_type" : ... ,
    "additional_info" : ...
}

"""

class Query_Reciever:
    def __init__(self):
        self.llm = OpenAI_LLM()
        self.PROMPT = query_receiver
    
    def add_prompt(self, prompt: str, database_schema : str) -> str:
        formatted_prompt = self.PROMPT.format(question=prompt, database_schema=database_schema)
        return formatted_prompt

    def parse_response(self, response: str):
        response = json.loads(response)
        return response

    def inference(self, usr_prompt: str, database_schema: str):
        formatted_prompt = self.add_prompt(usr_prompt, database_schema)
        return self.llm.run(formatted_prompt)
import json
from llm import OpenAI_LLM
from .prompts import planner




class Planner:
    def __init__(self):
        self.llm = OpenAI_LLM()
        self.PROMPT = planner
    
    def add_prompt(self, usr_prompt: str, database_schema : str) -> str:
        formatted_prompt = self.PROMPT.format(question=usr_prompt, database_schema=database_schema)
        return formatted_prompt

    def parse_response(self, response: str):
        response = json.loads(response)
        return response


    def inference(self, usr_prompt: str, database_schema: str):
        formatted_prompt = self.add_prompt(usr_prompt, database_schema)
        return self.llm.run(formatted_prompt)

import json
from llm import OpenAI_LLM
from .prompts import query_builder

class Query_Builder:
    def __init__(self):
        self.llm = OpenAI_LLM()
        self.PROMPT = query_builder
    
    def add_prompt(self, plan, database_schema : str) -> str:
        formatted_prompt = self.PROMPT.format(instructions=plan, database_schema=database_schema)
        return formatted_prompt
    
    def parse_response(self, response: str):
        result = json.loads(response)
        return result
        
    def inference(self, instructions : [{}], database_schema: str):
        formatted_prompt = self.add_prompt(instructions, database_schema)
        return self.llm.run(formatted_prompt)
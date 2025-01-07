from openai import OpenAI 
# from .config import get_openai_api, get_model_name
from utils.config import get_openai_api, get_model_name


class OpenAI_LLM:
    def __init__(self):
        api_key = get_openai_api()
        self.client = OpenAI(api_key = api_key)
    
    def run(self, usr_prompt : str):
        completion = self.client.chat.completions.create(
            model = get_model_name(),
            messages = [
                # {
                #     "role":"system",
                #     "content": sys_prompt

                # },
                {
                    "role": "user",
                    "content": usr_prompt
                }
            ],
            temperature = 0,
            seed = 435212
        )
        return completion.choices[0].message.content

# s =   "You are a helpful assistant. the output must be in JSON format"
# u =  "Hello!"

# l = OpenAI_LLM()
# result = l.run(model_name='gpt-3.5-turbo', usr_prompt=u)
# print(result)
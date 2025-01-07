from groq import Groq
from utils.config import get_groq_api, get_groq_model


class GROQ_LLM:
    def __init__(self):
        api_key = get_groq_api()
        self.client = Groq(api_key = api_key)
    
    def run(self, usr_prompt : str):
        completion = self.client.chat.completions.create(
            model = get_groq_model(),
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
            temperature = 0
        )
        return completion.choices[0].message.content
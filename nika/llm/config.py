import os 
from dotenv import load_dotenv

load_dotenv() 

def get_openai_api():
    # return os.getenv("api")
    return os.environ.get("api1")

def get_db_sql():
    return os.getenv("db_path")

def get_model_name():
    return os.getenv("model_name")
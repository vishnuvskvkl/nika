import os 
from dotenv import load_dotenv

load_dotenv() 

def get_openai_api():
    return os.environ.get("api_openai")

def get_model_name():
    return os.getenv("model_name")

def get_groq_api():
    return os.getenv("api_groq")

def get_groq_model():
    return os.getenv("model_groq")

database_connection = {
    "postgres": {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "database": os.getenv("POSTGRES_DB"),
        "schema": os.getenv("POSTGRES_SCHEMA")
    }
}
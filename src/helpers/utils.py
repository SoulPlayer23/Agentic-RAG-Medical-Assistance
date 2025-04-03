from dotenv import load_dotenv
import os

load_dotenv()

def get_model():
    return os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
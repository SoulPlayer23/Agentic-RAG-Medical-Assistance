from dotenv import load_dotenv
import os

load_dotenv()

def get_model(purpose: str):
    if purpose == "medical":
        return os.getenv('MODEL_CHOICE', 'gpt-4.1-mini')
    elif purpose == "agent":
        return 'gpt-4o-mini'
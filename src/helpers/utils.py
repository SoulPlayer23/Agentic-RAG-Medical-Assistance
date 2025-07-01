from dotenv import load_dotenv
import os

import pandas as pd

load_dotenv()

def get_model(purpose: str):
    if purpose == "medical":
        return os.getenv('MODEL_CHOICE', 'gpt-4.1-mini')
    elif purpose == "agent":
        return 'gpt-4o-mini'

def get_src_path():
    return os.getenv('BASE_PATH', '')

def load_auxiliary_disease_data():
    base_path = os.path.join(get_src_path(), 'src', 'data', 'diagnosis-dataset')
    print("Loading auxiliary disease data from:", base_path)
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Base path does not exist: {base_path}")
    return {
        'symptom_list': pd.read_csv(os.path.join(base_path, 'Training.csv')).drop(['prognosis'], axis=1).columns,
        'symptoms': pd.read_csv(os.path.join(base_path, 'symptoms_df.csv')),
        'precautions': pd.read_csv(os.path.join(base_path, 'precautions_df.csv')),
        'workout': pd.read_csv(os.path.join(base_path, 'workout_df.csv')).drop(columns=['Unnamed: 0', 'Unnamed: 1']),
        'description': pd.read_csv(os.path.join(base_path, 'description.csv')),
        'medications': pd.read_csv(os.path.join(base_path, 'medications.csv')),
        'diets': pd.read_csv(os.path.join(base_path, 'diets.csv')),
        'severity': pd.read_csv(os.path.join(base_path, 'Symptom-severity.csv')),
    }

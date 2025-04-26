import json
from typing import List
from agents import RunContextWrapper, function_tool
from context.user_context import UserContext


@function_tool
def diagnose(wrapper: RunContextWrapper[UserContext], symptoms: List[str]) -> str:
    """Retrieve patient details and analysis."""
    # Mock JSON data for demonstration purposes
    diagnosis_data = {
        "Flu": {
            "symptoms": ["fever", "cough", "sore throat"],
            "treatment": "Rest and hydration."
        },
        "COVID-19": {
            "symptoms": ["fever", "cough", "loss of taste"],
            "treatment": "Isolation and monitoring."
        },
        "Allergy": {
            "symptoms": ["sneezing", "itchy eyes"],
            "treatment": "Antihistamines."
        },
        "Migraine": {
            "symptoms": ["headache", "nausea"],
            "treatment": "Pain relief medication."
        },
        "Diabetes": {
            "symptoms": ["increased thirst", "frequent urination"],
            "treatment": "Insulin therapy."
        },
        "Hypertension": {
            "symptoms": ["headache", "nosebleeds"],
            "treatment": "Lifestyle changes and medication."
        },
        "Anxiety": {
            "symptoms": ["nervousness", "restlessness"],
            "treatment": "Therapy and medication."
        },
        "Depression": {
            "symptoms": ["sadness", "fatigue"],
            "treatment": "Therapy and medication."
        },
        "Asthma": {
            "symptoms": ["shortness of breath", "wheezing"],
            "treatment": "Inhalers and bronchodilators."
        },
        "Arthritis": {
            "symptoms": ["joint pain", "stiffness"],
            "treatment": "Pain relief and physical therapy."
        },
        "Heart Disease": {
            "symptoms": ["chest pain", "shortness of breath"],
            "treatment": "Lifestyle changes and medication."
        },
        "Stroke": {
            "symptoms": ["sudden numbness", "confusion"],
            "treatment": "Emergency medical care."
        },
        "Cancer": {
            "symptoms": ["unexplained weight loss", "fatigue"],
            "treatment": "Chemotherapy and radiation."
        }
    }

    for disease in diagnosis_data:
        if all(symptom in diagnosis_data[disease]["symptoms"] for symptom in symptoms):
            return json.dumps(diagnosis_data[disease])
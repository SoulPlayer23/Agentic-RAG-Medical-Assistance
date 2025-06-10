import ast
from typing import Any, List
from agents import RunContextWrapper, function_tool
import joblib
from pandas import Index
import pandas as pd
from pydantic import BaseModel
from context.user_context import UserContext
from models.tool_models import Diagnosis
from openai import OpenAI
from helpers.utils import get_model, get_src_path, load_auxiliary_disease_data

client = OpenAI()
AUX_DATA = None

class Recommendation_list(BaseModel):
    recommendations: List[str]

src_path = get_src_path()
model = joblib.load(src_path + r'src\ai_models\diagnosis_model.pkl')  # Load the pre-trained model
label_encoder = joblib.load(src_path + r'src\ai_models\label_encoder.pkl')  # Load the label encoder

@function_tool
def diagnose(wrapper: RunContextWrapper[UserContext], symptoms: List[str]):
    """Analyse symptoms and provide a diagnosis."""
    aux_data = get_auxiliary_data()
    diagnosis_data = analyze_symptoms(symptoms, aux_data)
    return diagnosis_data
        
def get_auxiliary_data():
    global AUX_DATA
    if AUX_DATA is None:
        AUX_DATA = load_auxiliary_disease_data()
    return AUX_DATA

def analyze_symptoms(input_symptoms: List[str], aux_data: dict[str, Any]) -> Diagnosis:
    """Analyze the provided symptoms and return a diagnosis."""

    symptoms_list = aux_data['symptom_list']
    symptom_severity = dict(zip(aux_data['severity']['Symptom'], AUX_DATA['severity']['weight']))
    disease_list = label_encoder.classes_.tolist()

    symptom_vector = get_symptoms(input_symptoms, symptoms_list, symptom_severity)
    predicted_disease = predict_disease(symptom_vector)
    disease_description, disease_precautions, disease_medications, disease_diet, disease_workout = get_disease_info(predicted_disease, disease_list)

    recommendations(input_symptoms, predicted_disease, disease_description, disease_precautions, disease_medications, disease_workout, disease_diet)

    return Diagnosis(
        symptoms=input_symptoms,
        diagnosis=predicted_disease + disease_description,
        precautions=disease_precautions,
        medications=disease_medications,
        workouts=disease_workout,
        diet=disease_diet,
        recommendations=recommendations(input_symptoms, predicted_disease, disease_description, disease_precautions, disease_medications, disease_workout, disease_diet)
    )

def get_symptoms(input_symptoms: List[str], symptoms_list: Index, symptom_severity: dict[str, int]):
    print(f"\nInput Symptoms: {input_symptoms}")
    input_symptoms = [symptom.replace(' ', '_').lower().strip() for symptom in input_symptoms]
    if not input_symptoms:
        print("No symptoms entered. Please try again.")
        return None

    input_vector = {col: 0 for col in symptoms_list}  # Initialize input vector with zeros
    for symptom in input_symptoms:
        if symptom in symptoms_list:
            input_vector[symptom] = symptom_severity.get(symptom, 1)  # Default severity to 1 if not found
        else:
            print(f"Symptom '{symptom}' not recognized. Please check the spelling or try a different symptom.")
    input_vector = pd.DataFrame([input_vector])  # Convert to DataFrame for prediction
    return input_vector

def predict_disease(input_vector):
    prediction = model.predict(input_vector)[0]  # Get the predicted class index
    predicted_disease = label_encoder.inverse_transform([prediction])[0]
    print("Predicted Disease:", predicted_disease)
    return predicted_disease

def get_disease_info(disease_name, disease_list):
    if disease_name in disease_list:
        disease_description = AUX_DATA['description'][AUX_DATA['description']['Disease'] == disease_name]['Description']
        disease_description = " ".join([w for w in disease_description])
    
        disease_precautions = AUX_DATA['precautions'][AUX_DATA['precautions']['Disease'] == disease_name][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
        disease_precautions = disease_precautions.values.flatten().tolist()

        medications = AUX_DATA['medications'][AUX_DATA['medications']['Disease'] == disease_name]['Medication'].tolist()
        disease_medications = ast.literal_eval(medications[0]) if medications else []

        diets = AUX_DATA['diets'][AUX_DATA['diets']['Disease'] == disease_name]['Diet'].tolist()
        disease_diet = ast.literal_eval(diets[0]) if diets else []
        
        disease_workout = AUX_DATA['workout'][AUX_DATA['workout']['disease'] == disease_name]['workout'].tolist()

        return disease_description, disease_precautions, disease_medications, disease_diet, disease_workout
    else:
        print(f"Disease '{disease_name}' not found in the dataset.")
        return None
    
def recommendations(input_symptoms, predicted_disease, disease_description, disease_precautions, disease_medications, disease_workout, disease_diet) -> list[str]:
    prompt = (f"Diagnosis details:\n"
        f"Symptoms: {input_symptoms}\n"
        f"Disease: {predicted_disease}\n"
        f"Description: {disease_description}\n"
        f"Precautions: {', '.join(disease_precautions)}\n"
        f"Medications: {', '.join(disease_medications)}\n"
        f"Workouts: {', '.join(disease_workout)}\n"
        f"Diet: {', '.join(disease_diet)}\n\n"
        "Based on the above, provide a brief medical recommendation in no more than 3 points.")
    response = client.responses.parse(
        model=get_model("medical"),
        input=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt}
        ],
        text_format=Recommendation_list,
        max_output_tokens=128,
        temperature=0.2
    )
    return response.output_parsed.recommendations
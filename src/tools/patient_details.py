import json
from typing import List
from pydantic import BaseModel
from agents import RunContextWrapper, function_tool
from openai import OpenAI
from qdrant_client import QdrantClient, models
from qdrant_client.conversions import common_types as types
from context.user_context import UserContext
from helpers.utils import get_model
from models.tool_models import PatientResponse

client = OpenAI()
qdrant_client = QdrantClient(host="homeserver", port=6333, prefer_grpc=True)
collection_name = "patient_data"

class Recommendation_list(BaseModel):
    recommendations: List[str]

@function_tool
def patient_retriever(wrapper: RunContextWrapper[UserContext], query: str, query_type: str):
    """Retrieve patient details and analysis."""
    if query_type == "patient_id":
        results = search_patient(patient_id=query)
    elif query_type == "patient_name":
        results = search_patient(patient_name=query)
    else:
        results = search_patient(query_text=query)

    patient_data = [patient for patient in results]

    if not patient_data:
        return json.dumps({"error": "No patient data found."})
    
    for patient in patient_data:
        prompt = (f"Patient details:\n"
            f"Name: {patient['patient_name']}\n"
            f"Age: {patient['age']}\n"
            f"Gender: {patient['gender']}\n"
            f"Medical History: {', '.join(patient['medical_history'])}\n"
            f"Lab Reports: {', '.join(patient['lab_reports'])}\n"
            f"Diagnosis: {patient['diagnosis']}\n\n"
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
        patient['recommendations'] = response.output_parsed.recommendations

    patient_data = [PatientResponse(**patient) for patient in patient_data]

    return patient_data
    
def search_patient(query_text=None, patient_id=None, patient_name=None, limit=5):
    # Generate embedding for text queries
    if query_text:
        query_vector = get_embedding(query_text)
    else:
        query_vector = None  # For exact filtering

    # Filter by exact fields (patient_id, patient_name)
    # Qdrant expects filter conditions as a list of dicts with 'field' and 'match', not as protobuf objects or with 'key'.
    filter_conditions = []
    if patient_id:
        filter_conditions.append(
            models.FieldCondition(
                key="patient.patient_id",
                match=models.MatchValue(value=patient_id)
            ))
    if patient_name:
        filter_conditions.append(
            models.FieldCondition(
                key="patient.patient_name",
                match=models.MatchValue(value=patient_name)
            ))
        
    qdrant_filter_model = models.Filter(must=filter_conditions) if filter_conditions else None

    # Use correct Qdrant search signature: always provide query_vector as first argument
    if query_vector is not None:
        results = qdrant_client.query_points(
            collection_name="patients",
            query=query_vector,
            query_filter=qdrant_filter_model,
            limit=limit
        )
    elif qdrant_filter_model:
        # For filter-only search, use a dummy vector (e.g., zeros) and set score_threshold very low
        points_page, _ = qdrant_client.scroll(
            collection_name="patients",
            scroll_filter=qdrant_filter_model,
            limit=limit
        )
        results = points_page
    else:
        return []

    # Deduplicate results by patient_id
    unique_patients = {}
    if isinstance(results, list) and all(isinstance(r, types.Record) for r in results):
        for idx, record in enumerate(results, 1):
            patient = record.payload.get("patient")
            unique_patients[patient["patient_id"]] = patient
    elif isinstance(results, types.QueryResponse):
        for scored_point in results.points:
            patient = scored_point.payload.get("patient")
            unique_patients[patient["patient_id"]] = patient

    return list(unique_patients.values())

def get_embedding(text):
    return client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    ).data[0].embedding
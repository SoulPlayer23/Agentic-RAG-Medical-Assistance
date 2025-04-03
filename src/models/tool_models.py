from typing import List
from pydantic import BaseModel, Field

# Model for PubMed Retriever
class PubMedResponse(BaseModel):
    title: str
    abstract: str
    citations: List[str]

# Model for Patient Retriever
class PatientResponse(BaseModel):
    patient_id: str
    patient_name: str
    age: int
    gender: str
    medical_history: List[str]
    lab_reports: List[str]
    diagnosis: str
    recommendations: List[str]
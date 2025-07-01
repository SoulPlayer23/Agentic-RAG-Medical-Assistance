from typing import List
from pydantic import BaseModel, Field

# Model for PubMed Retriever
class PubMedResponse(BaseModel):
    title: str
    abstract: str

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

# Model for Diagnosis
class Diagnosis(BaseModel):
    symptoms: List[str]
    diagnosis: str
    description: str = Field(description="Detailed description of the diagnosis.")
    precautions: List[str] = Field(description="Precautions to take based on the diagnosis.")
    medications: List[str] = Field(description="Medications recommended for the diagnosis.")
    workouts: List[str] = Field(description="Recommended workouts for the patient.")
    diet: List[str] = Field(description="Dietary recommendations for the patient.")
    recommendations: List[str] = Field(description="Recommendations for the patient based on the diagnosis.")

# Model for Report Analysis
class ReportAnalysis(BaseModel):
    analysis: str
    recommendations: List[str] = Field(description="Recommendations based on the analysis.")

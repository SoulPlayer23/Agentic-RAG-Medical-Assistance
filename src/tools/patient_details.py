import json
from agents import RunContextWrapper, function_tool
from context.user_context import UserContext


@function_tool
def patient_retriever(wrapper: RunContextWrapper[UserContext], patient_id: str) -> str:
    """Retrieve patient details and analysis."""
    # Mock JSON data for demonstration purposes
    patient_data = {
        "123": {
            "name": "John Doe",
            "age": 30,
            "gender": "Male",
            "medical_history": ["Diabetes", "Hypertension"],
            "lab_reports": ["Blood test results", "MRI scan"],
            "diagnosis": "Diabetes",
            "recommendations": ["Change diet", "Take medication"],
        },
        "456": {
            "name": "Jane Smith",
            "age": 25,
            "gender": "Female",
            "medical_history": ["Hypertension", "Asthma"],
            "lab_reports": ["Blood test results", "X-ray"],
            "diagnosis": "Hypertension",
            "recommendations": ["Change diet", "Take medication"],
        },
        "789": {
            "name": "Michael Johnson",
            "age": 40,
            "gender": "Male",
            "medical_history": ["Diabetes", "Asthma"],
            "lab_reports": ["Blood test results", "MRI scan"],
            "diagnosis": "Diabetes",
            "recommendations": ["Change diet", "Take medication"],
        }
    }
    if patient_id in patient_data:
        return json.dumps(patient_data[patient_id])
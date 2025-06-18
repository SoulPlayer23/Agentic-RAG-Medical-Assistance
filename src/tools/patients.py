import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from agents import RunContextWrapper, function_tool
from openai import OpenAI
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType, Filter, FieldCondition, MatchValue
from qdrant_client.conversions import common_types as types
from context.user_context import UserContext
from helpers.utils import get_model
from models.tool_models import PatientResponse
import numpy as np

# Initialize clients with proper configuration
try:
    client = OpenAI()
    qdrant_client = QdrantClient(
        host="homeserver",
        port=6333,
        prefer_grpc=True,
        timeout=10.0  # Add reasonable timeout
    )
    
    # Ensure collection exists with proper configuration
    collection_name = "patients"
    if not qdrant_client.collection_exists(collection_name):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small dimension
                distance=Distance.COSINE
            ),
            # Add payload indexing for faster filtering
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=0,  # Index all points
            ),
            # Define payload schema for efficient filtering
            on_disk_payload=True,  # Store payload on disk for large datasets
        )
        # Add payload schema
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="patient.patient_id",
            field_schema=PayloadSchemaType.KEYWORD
        )
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="patient.patient_name",
            field_schema=PayloadSchemaType.TEXT  # Enable full-text search
        )
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="patient.medical_history",
            field_schema=PayloadSchemaType.TEXT  # Enable full-text search
        )
except Exception as e:
    print(f"Error initializing clients: {str(e)}")
    raise

class Recommendation_list(BaseModel):
    recommendations: List[str]

@function_tool
def patient_retriever(wrapper: RunContextWrapper[UserContext], query: str, query_type: str):
    """Retrieve patient details and analysis with advanced filtering and scoring.
    
    Args:
        wrapper: The context wrapper
        query: The search query (can be id, name, or general text)
        query_type: Type of query ('patient_id', 'patient_name', or 'text')
    
    Returns:
        List of matching patient records with recommendations
    """
    try:
        if query_type == "patient_id":
            results = search_patient(patient_id=query)
        elif query_type == "patient_name":
            results = search_patient(patient_name=query)
        else:
            # For general text search, use vector similarity with metadata boost
            results = search_patient(query_text=query)

        if not results:
            return json.dumps({"error": "No patient data found matching your query."})

        # Process results and generate recommendations
        enriched_results = []
        for patient in results:
            try:
                # Prepare comprehensive patient summary
                summary = create_patient_summary(patient)
                recommendations = generate_recommendations(summary)
                patient['recommendations'] = recommendations
                enriched_results.append(PatientResponse(**patient))
            except Exception as e:
                print(f"Error processing patient {patient.get('patient_id')}: {str(e)}")
                continue

        return enriched_results

    except Exception as e:
        print(f"Error in patient_retriever: {str(e)}")
        return json.dumps({"error": f"Error retrieving patient data: {str(e)}"})

def search_patient(query_text: Optional[str] = None,
                 patient_id: Optional[str] = None,
                 patient_name: Optional[str] = None,
                 limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for patients using advanced vector search and metadata filtering.
    
    Args:
        query_text: General text query for semantic search
        patient_id: Exact patient ID for direct lookup
        patient_name: Patient name for text search
        limit: Maximum number of results to return
    """
    try:
        # Initialize filter conditions
        filter_conditions = []
        
        # Add exact match filters
        if patient_id:
            filter_conditions.append(
                FieldCondition(
                    key="patient.patient_id",
                    match=MatchValue(value=patient_id)
                )
            )
            
        if patient_name:
            # Use text match for names to handle partial matches
            filter_conditions.append(
                FieldCondition(
                    key="patient.patient_name",
                    match=MatchValue(value=patient_name)
                )
            )

        # Create filter if conditions exist
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Handle different search scenarios
        if query_text:
            # Get embedding for semantic search
            query_vector = get_embedding(query_text)
            
            # Perform vector search with metadata filtering
            results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit,
                with_payload=True,  # Include full payload
                with_vectors=False,  # No need for vectors in response
            )
            
            # Process scored results
            return [
                point.payload["patient"]
                for point in results
                if "patient" in point.payload
            ]
            
        elif search_filter:
            # For filter-only search (exact matches)
            scroll_results, _ = qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=search_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            # Process unscored results
            return [
                point.payload["patient"]
                for point in scroll_results
                if "patient" in point.payload
            ]
            
        else:
            return []
            
    except Exception as e:
        print(f"Error in search_patient: {str(e)}")
        return []

def get_embedding(text):
    return client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    ).data[0].embedding

def create_patient_summary(patient: Dict[str, Any]) -> str:
    """Create a comprehensive patient summary for recommendation generation."""
    return (f"Patient details:\n"
            f"Name: {patient['patient_name']}\n"
            f"Age: {patient['age']}\n"
            f"Gender: {patient['gender']}\n"
            f"Medical History: {', '.join(patient['medical_history'])}\n"
            f"Lab Reports: {', '.join(patient['lab_reports'])}\n"
            f"Diagnosis: {patient['diagnosis']}")

def generate_recommendations(summary: str) -> List[str]:
    """Generate medical recommendations based on patient summary."""
    try:
        response = client.responses.parse(
            model=get_model("medical"),
            input=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": f"{summary}\n\nBased on the above, provide a brief medical recommendation in no more than 3 points."}
            ],
            text_format=Recommendation_list,
            max_output_tokens=128,
            temperature=0.2
        )
        return response.output_parsed.recommendations
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return ["Unable to generate recommendations due to an error."]
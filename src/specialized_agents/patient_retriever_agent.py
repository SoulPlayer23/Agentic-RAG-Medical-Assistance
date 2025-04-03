from agents import Agent

from helpers.utils import get_model
from models.tool_models import PatientResponse
from tools.patient_details import patient_retriever
from prompts.specialized_agent_prompts import patient_retriever_prompt

patient_retriever_agent = Agent(
    name="Patient Retriever",
    handoff_description="Retrieve patient details and analysis.",
    instructions=patient_retriever_prompt,
    model=get_model(),
    tools=[patient_retriever],
    output_type=PatientResponse
)
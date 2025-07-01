from agents import Agent
from helpers.utils import get_model
from models.orchestrator_models import StructuredResponse
from prompts.specialized_agent_prompts import follow_up_agent_prompt

follow_up_agent = Agent(
    name="Follow Up Agent",
    instructions=follow_up_agent_prompt,
    handoff_description="Follow up on a patient query",
    model=get_model("medical"),
    output_type=StructuredResponse
)
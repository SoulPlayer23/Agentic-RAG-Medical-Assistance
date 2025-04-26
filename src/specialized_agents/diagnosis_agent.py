from agents import Agent

from helpers.utils import get_model
from models.tool_models import Diagnosis
from tools.diagnose import diagnose
from prompts.specialized_agent_prompts import diagnosis_prompt

diagnose_agent = Agent(
    name="Diagnosis",
    handoff_description="Diagnose based on symptoms provided.",
    instructions=diagnosis_prompt,
    tools=[diagnose],
    output_type=Diagnosis
)
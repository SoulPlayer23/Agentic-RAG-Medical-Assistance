from agents import Agent

from helpers.utils import get_model
from models.guardrail_models import QueryAnalysis
from prompts.specialized_agent_prompts import query_analysis_prompt

query_analysis_agent = Agent(
    name="Query Analysis Agent",
    instructions=query_analysis_prompt,
    output_type=QueryAnalysis,
    model=get_model()
)
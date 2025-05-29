from agents import Agent

from helpers.utils import get_model
from models.tool_models import ReportAnalysis
from specialized_agents.support_agents import pdf_analysis_agent, image_analysis_agent
from prompts.specialized_agent_prompts import report_analysis_prompt

report_analysis_agent = Agent(
    name="Report Analyzer",
    instructions=report_analysis_prompt,
    model=get_model("agent"),
    handoffs=[pdf_analysis_agent, image_analysis_agent],
    output_type=ReportAnalysis
)
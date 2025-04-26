from agents import Agent

from helpers.utils import get_model
from models.tool_models import ReportAnalysis
from tools.analyze_report import analyze_report
from prompts.specialized_agent_prompts import report_analysis_prompt

report_analysis_agent = Agent(
    name="Report Analyzer",
    handoff_description="Analyse a patient report or medical scan.",
    instructions=report_analysis_prompt,
    model=get_model(),
    tools=[analyze_report],
    output_type=ReportAnalysis
)
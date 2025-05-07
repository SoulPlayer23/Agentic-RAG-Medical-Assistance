from agents import Agent
from helpers.utils import get_model
from models.tool_models import ReportAnalysis
from prompts.specialized_agent_prompts import pdf_analysis_agent_prompt
from prompts.specialized_agent_prompts import image_analysis_agent_prompt
from tools.analyze_pdf_report import analyze_pdf_report
from tools.analyze_image_scan import analyze_image_scan

pdf_analysis_agent = Agent(
    name="PDF Analyzer",
    handoff_description="Analyse a patient PDF medical report",
    instructions=pdf_analysis_agent_prompt,
    tools=[analyze_pdf_report],
    model=get_model(),
    output_type=ReportAnalysis
)

image_analysis_agent = Agent(
    name="Image Analyzer",
    handoff_description="Analyse a patient image medical scan",
    instructions=image_analysis_agent_prompt,
    tools=[analyze_image_scan],
    model=get_model(),
    output_type=ReportAnalysis
)
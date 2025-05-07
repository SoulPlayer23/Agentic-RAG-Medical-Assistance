import base64
import json
from agents import RunContextWrapper, function_tool
import fitz
from openai import OpenAI
from context.user_context import UserContext
from helpers.utils import get_model
from models.tool_models import ReportAnalysis
from prompts.specialized_agent_prompts import pdf_analysis_prompt

client = OpenAI()

@function_tool
async def analyze_pdf_report(wrapper: RunContextWrapper[UserContext], query: str):
    if wrapper and wrapper.context:
        if wrapper.context.attachment and wrapper.context.attachment_type:

            attachment_type = wrapper.context.attachment_type

            if attachment_type == "application/pdf":
                analysis = await pdf_report_analysis(query, wrapper.context)
                return analysis
            
            else:
                return "Unsupported attachment type."
        else:
            return "No attachment found."
    else:
        return "No context found."
    
async def pdf_report_analysis(query: str, context: UserContext):
    
    pdf_filename = context.attachment.name
    encoded_pdf = base64.b64encode(context.attachment.read()).decode('utf-8')

    input = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file", 
                        "filename": pdf_filename,
                        "file_data": f"data:application/pdf;base64,{encoded_pdf}",
                    },
                    {
                        "type": "input_text", 
                        "text": f""" 
                            {pdf_analysis_prompt}

                            Query:
                            {query}
                        """
                    }
                ]
            }
        ]

    response = client.responses.parse(
        model=get_model(),
        input=input,
        text_format=ReportAnalysis
    )

    analysis = response.output_parsed
    print(analysis)

    return analysis
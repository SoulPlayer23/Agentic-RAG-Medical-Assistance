import base64
import json
from agents import RunContextWrapper, function_tool
from  PIL import Image
from openai import OpenAI

from context.user_context import UserContext
from helpers.utils import get_model
from models.tool_models import ReportAnalysis
from prompts.specialized_agent_prompts import image_analysis_prompt

client = OpenAI()

@function_tool
async def analyze_image_scan(wrapper: RunContextWrapper[UserContext], query: str):
    if wrapper and wrapper.context:
        if wrapper.context.attachment and wrapper.context.attachment_type:

            attachment_type = wrapper.context.attachment_type

            if attachment_type == "image/jpeg" or attachment_type == "image/jpg" or attachment_type == "image/png":
                analysis = await image_scan_analysis(query, wrapper.context)
                return analysis
            
            else:
                return "Unsupported attachment type."
        else:
            return "No attachment found."
    else:
        return "No context found."

async def image_scan_analysis(query: str, context: UserContext):

    encoded_image = base64.b64encode(context.attachment.read()).decode('utf-8')

    input = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f""" 
                        {image_analysis_prompt}

                        Query:
                        {query}
                    """},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ]
            }
        ]

    response = client.responses.parse(
        model=get_model(),
        input=input,
        text_format=ReportAnalysis
    )

    return response.output_parsed
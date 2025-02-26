import asyncio
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from components.pubmed_retriever import pubmed_retriever
from components.diagnose import diagnose
from components.analyze_report import analyze_report
from components.patient_details import patient_details
from prompts.agent import agent_prompt

ollama_model = OpenAIModel(
    model_name="llama3.2:latest",
    base_url="http://localhost:11434/v1"
)

agent = Agent(
    ollama_model,
    deps_type=str,
    retries=2,
    system_prompt=agent_prompt
    )

@agent.tool
def retrieve_from_pubmed(ctx: RunContext, query):
    return pubmed_retriever(query, ctx)

@agent.tool
def diagnose_patient(ctx: RunContext, symptoms):
    return diagnose(symptoms, ctx)

@agent.tool
def report_analysis(ctx: RunContext, report):
    return analyze_report(report, ctx)

@agent.tool
def patient_analysis(ctx: RunContext, patient):
    return patient_details(patient, ctx)

async def main():
    user_inputs = [
        "I need to know what are the latest guidelines to treat tuberculosis."
    ]
    
    for user_input in user_inputs:
        response = await agent.run(user_input)
        print(f"User Input: {user_input}")
        print(f"Agent Response: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
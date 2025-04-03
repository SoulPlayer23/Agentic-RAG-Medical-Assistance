import asyncio
import os
from agents import Agent, GuardrailFunctionOutput, InputGuardrail, InputGuardrailTripwireTriggered, Runner, set_tracing_export_api_key
from dotenv import load_dotenv

from prompts.orchestrator_prompt import orchestrator_agent_prompt

from models.orchestrator_models import StructuredResponse
from models.guardrail_models import QueryAnalysis

from context.user_context import UserContext

from specialized_agents.query_analysis_agent import query_analysis_agent
from specialized_agents.pubmed_retriever_agent import pubmed_retriever_agent
from specialized_agents.patient_retriever_agent import patient_retriever_agent

# Load environment variables
load_dotenv()



# Set tracing export API key if needed
set_tracing_export_api_key(os.getenv('OPENAI_API_KEY'))

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

# Guardrails

async def medical_guardrail(ctx, agent, input_data):
    """Check if the input data is related to medical queries."""
    try:
        analysis_prompt = f"The user is asking '{input_data}'. \nAnalyze if their query is related to medical queries."
        result = await Runner.run(query_analysis_agent, analysis_prompt, context=ctx.context)
        final_output = result.final_output_as(QueryAnalysis)

        if not final_output.medical:
            print(f"\nThis query is not related to medical topics. Reasoning: {final_output.reasoning}" if not final_output.medical else None)

        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.medical
        )
    except Exception as e:
        return GuardrailFunctionOutput(
            output_info=QueryAnalysis(medical=True, reasoning=f"Error analyzing query: {str(e)}"),
            tripwire_triggered=False
        )

# Orchestrator agent

orchestrator_agent = Agent(
    name="Orchestrator Agent",
    instructions=orchestrator_agent_prompt,
    model = model,
    handoffs=[pubmed_retriever_agent, patient_retriever_agent],
    input_guardrails=[InputGuardrail(guardrail_function=medical_guardrail)],
    output_type=StructuredResponse
)

async def main():

    # Create user context
    user_context = UserContext(
        user_id="user123",
    )

    queries = [
        "Is there any new research on Diabetes?",
        "Does patient 456 have any allergies?",
        "Where is leaning tower of pisa located?",
    ]

    for query in queries:
        print("\n" + "-" * 50)
        print(f"User Query: {query}")

        try:
            result = await Runner.run(orchestrator_agent, query, context=user_context)
        
            print("\nFINAL RESPONSE:")
            
            # Format the output based on the type of response
            if hasattr(result.final_output, "title"):
                pubmed_response = result.final_output
                print("\n 📄 PUBMED RESEARCH PAPER 📄")
                print(f"Title: {pubmed_response.title}")
                print(f"Abstract: {pubmed_response.abstract}")
                print("\nCitations:")
                for citation in pubmed_response.citations:
                    print(f"  - {citation}")
                
            elif hasattr(result.final_output, "patient_id") and hasattr(result.final_output, "patient_name"):
                patient = result.final_output
                print("\n 🏥 PATIENT DETAILS 🏥")
                print(f"Patient ID: {patient.patient_id}")
                print(f"Name: {patient.patient_name}")
                print(f"Age: {patient.age}")
                print(f"Gender: {patient.gender}")
                print("\nMedical History:")
                for i, history in enumerate(patient.medical_history, 1):
                    print(f"  {i}. {history}")
                print("\nLab Reports:")
                for i, report in enumerate(patient.lab_reports, 1):
                    print(f"  {i}. {report}")
                print(f"\nDiagnosis: {patient.diagnosis}")
                print("\nRecommendations:")
                for i, recommendation in enumerate(patient.recommendations, 1):
                    print(f"  {i}. {recommendation}")
            
            else:  # Generic response
                print(result.final_output)

        except InputGuardrailTripwireTriggered as e:
            print("\n⚠️ GUARDRAIL TRIGGERED ⚠️")


if __name__ == "__main__":
    asyncio.run(main())
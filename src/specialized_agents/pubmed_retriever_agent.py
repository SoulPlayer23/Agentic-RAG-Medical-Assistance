from agents import Agent

from helpers.utils import get_model
from models.tool_models import PubMedResponse
from tools.pubmed_retriever import retrieve_from_pubmed
from prompts.specialized_agent_prompts import pubmed_retriever_prompt

pubmed_retriever_agent = Agent(
    name="PubMed Retriever",
    handoff_description="Retrieve relevant medical research papers from PubMed.",
    instructions=pubmed_retriever_prompt,
    model=get_model("agent"),
    tools=[retrieve_from_pubmed],
    output_type=list[PubMedResponse]
)
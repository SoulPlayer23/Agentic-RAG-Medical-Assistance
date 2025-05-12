from agents import function_tool, RunContextWrapper
from context.user_context import UserContext
import json
from pymed import PubMed

from models.tool_models import PubMedResponse

@function_tool
def retrieve_from_pubmed(wrapper: RunContextWrapper[UserContext],keyword: str) -> list[PubMedResponse]:
    """Retrieve relevant medical research papers from PubMed based on the user's query."""
    from_date = wrapper.context.from_date.strftime("%Y/%m/%d")
    to_date = wrapper.context.to_date.strftime("%Y/%m/%d")
    top_n_papers = int(wrapper.context.preferred_number_of_papers)
    
    results = fetch_papers(from_date, to_date, top_n_papers, keyword)
    
    return results
    
def fetch_papers(from_date: str, to_date: str, top_n_papers: int, keyword: str):
    pubmed_client = PubMed(tool="PubMedRetriever", email="venkiteshsa@gmail.com")
    query = f'(("{from_date}"[Date - Publication] : "{to_date}"[Date - Publication])) AND ({keyword}[Text Word])'
    print(f"Query: {query}")
    results = pubmed_client.query(query, max_results=top_n_papers)
    papers = list(results)
    pubmed_responses = []
    for paper in papers:
        response = PubMedResponse(
            title=paper.title,
            abstract=paper.abstract
        )
        pubmed_responses.append(response)
    return pubmed_responses
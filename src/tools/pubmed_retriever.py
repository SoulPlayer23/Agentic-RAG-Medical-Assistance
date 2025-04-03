from agents import function_tool, RunContextWrapper
from context.user_context import UserContext
import json

@function_tool
def retrieve_from_pubmed(wrapper: RunContextWrapper[UserContext],keyword: str) -> str:
    """Retrieve relevant medical research papers from PubMed based on the user's query."""
    # Mock JSON data for demonstration purposes
    pubmed_data = {
        "Diabetes": {
            "title": "Latest Treatments for Diabetes",
            "abstract": "This paper discusses the latest treatments for diabetes.",
            "citations": ["paper-a", "paper-b"],
        },
        "Lung Cancer": {
            "title": "Advancements in treatment of Lung Cancer",
            "abstract": "This paper discusses advancements in treatment of Lung Cancer.",
            "citations": ["paper-x", "paper-y"],
        },
        "MRI Scans": {
            "title": "Innovations in MRI Scans",
            "abstract": "This paper discusses innovations in MRI scans.",
            "citations": ["paper-z"],
        },
        "Ebola": {
            "title": "Ebola Virus Disease",
            "abstract": "This paper discusses the Ebola virus disease.",
            "citations": ["paper-1", "paper-2"],
        }
    }
    if keyword in pubmed_data:
        return json.dumps(pubmed_data[keyword])
from agents import RunContextWrapper, function_tool
from context.user_context import UserContext

@function_tool
def analyze_report(wrapper: RunContextWrapper[UserContext], query: str):
    """
    Placeholder for analyze report
    """
    return f"Analysis for '{query}' is being retieved"
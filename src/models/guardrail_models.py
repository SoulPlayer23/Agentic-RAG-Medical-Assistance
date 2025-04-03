from pydantic import BaseModel

class QueryAnalysis(BaseModel):
    medical: bool
    reasoning: str
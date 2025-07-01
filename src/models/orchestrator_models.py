from typing import List
from pydantic import BaseModel, Field

# Model for structured output
class StructuredResponse(BaseModel):
    response: str
    assertion: str
    confidence: float = Field(description="Confidence level of the response (0 to 1).")
    additional_info: List[str] = Field(description="Any additional information or context related to the response.")
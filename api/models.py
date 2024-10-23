from pydantic import BaseModel
from typing import List, Optional

class Query(BaseModel):
    text: str
    max_responses: Optional[int] = 3

class PolicyResponse(BaseModel):
    statement: str
    score: float
    source: str
    context: List[str]
    topics: List[str]

class AnalysisResponse(BaseModel):
    responses: List[PolicyResponse]
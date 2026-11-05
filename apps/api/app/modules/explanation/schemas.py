from typing import Optional
import enum
from pydantic import BaseModel, Field


class ExplanationType(str, enum.Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    DEFINE = "define"
    EXAMPLE = "example"
    TRANSLATE = "translate"
    MAIN_IDEA = "main_idea"


class ExplainRequest(BaseModel):
    passage: str = Field(..., min_length=2, max_length=5000)
    explanation_type: ExplanationType = ExplanationType.SIMPLE
    document_id: Optional[str] = None
    page_number: Optional[int] = None


class ExplainResponse(BaseModel):
    explanation: str
    explanation_type: str
    passage_preview: str

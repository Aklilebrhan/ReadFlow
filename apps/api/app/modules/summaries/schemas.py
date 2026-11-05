from typing import Optional, List
import enum
from pydantic import BaseModel, Field


class SummaryType(str, enum.Enum):
    QUICK = "quick"
    DETAILED = "detailed"
    CHAPTERS = "chapters"
    KEY_POINTS = "key_points"
    ARGUMENTS = "arguments"
    FINDINGS = "findings"
    CONCLUSIONS = "conclusions"


class SummaryRequest(BaseModel):
    document_id: str
    summary_type: SummaryType = SummaryType.QUICK
    custom_instructions: Optional[str] = None


class SectionSummary(BaseModel):
    title: str
    summary: str
    page_range: Optional[str] = None


class SummaryResponse(BaseModel):
    document_id: str
    document_title: str
    summary_type: str
    summary: str
    sections: List[SectionSummary] = Field(default_factory=list)
    word_count: int = 0
    is_hierarchical: bool = False

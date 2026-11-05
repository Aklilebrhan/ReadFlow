from typing import Optional, List, Any, Dict
import enum
from pydantic import BaseModel, Field


class StudyMaterialType(str, enum.Enum):
    FLASHCARDS = "flashcards"
    QUIZ = "quiz"
    KEY_TERMS = "key_terms"
    NOTES = "notes"


class StudyRequest(BaseModel):
    document_id: str
    material_type: StudyMaterialType = StudyMaterialType.FLASHCARDS
    page_number: Optional[int] = None
    count: int = 5


class Flashcard(BaseModel):
    front: str
    back: str


class QuizOption(BaseModel):
    index: int
    text: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str


class KeyTerm(BaseModel):
    term: str
    definition: str
    context: Optional[str] = None


class StudyResponse(BaseModel):
    document_id: str
    document_title: str
    material_type: str
    items: List[Dict[str, Any]] = Field(default_factory=list)
    notes_content: Optional[str] = None

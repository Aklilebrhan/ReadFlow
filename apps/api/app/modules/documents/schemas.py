from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class CollectionResponse(CollectionBase):
    id: str
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    collection_id: Optional[str] = None


class DocumentCreate(DocumentBase):
    filename: str
    file_type: str
    file_size: int
    storage_path: str


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    collection_id: Optional[str] = None


class DocumentStatusResponse(BaseModel):
    id: str
    status: str
    status_message: Optional[str] = None
    progress_percent: int = 0


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: int
    section_title: Optional[str] = None
    text: str
    word_count: int

    model_config = ConfigDict(from_attributes=True)


class PageContent(BaseModel):
    page_number: int
    text: str
    word_count: int
    headings: List[str] = Field(default_factory=list)


class DocumentContentResponse(BaseModel):
    id: str
    title: str
    file_type: str
    page_count: int
    word_count: int
    pages: List[PageContent] = Field(default_factory=list)
    raw_text: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    status_message: Optional[str] = None
    progress_percent: int = 0
    page_count: int = 1
    word_count: int = 0
    collection: Optional[CollectionResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentHighlightCreate(BaseModel):
    page_number: int = 1
    selected_text: str = Field(..., min_length=1)
    color: str = "yellow"
    note: Optional[str] = None


class DocumentHighlightResponse(BaseModel):
    id: str
    document_id: str
    page_number: int
    selected_text: str
    color: str
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

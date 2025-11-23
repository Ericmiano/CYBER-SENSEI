from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KnowledgeDocumentBase(BaseModel):
    filename: str
    file_path: str
    doc_type: str = "document"
    status: str = "registered"
    transcript: Optional[str] = None
    notes: Optional[str] = None


class KnowledgeDocumentCreate(BaseModel):
    file_path: str
    username: Optional[str] = None
    display_name: Optional[str] = None


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True



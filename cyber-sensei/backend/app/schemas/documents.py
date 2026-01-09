from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=1000)
    content: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=1000)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None


class DocumentRead(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str]
    tags: Optional[List[str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

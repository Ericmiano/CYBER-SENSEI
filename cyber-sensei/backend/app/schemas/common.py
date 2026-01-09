from pydantic import BaseModel, Field
from typing import Optional


class QuizAnswer(BaseModel):
    question_id: int
    answer: str = Field(..., min_length=1)


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    search_type: Optional[str] = Field(None)
    limit: Optional[int] = Field(10, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field("desc")

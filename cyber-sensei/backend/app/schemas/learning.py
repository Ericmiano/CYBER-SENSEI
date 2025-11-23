from pydantic import BaseModel

class LearningStepResponse(BaseModel):
    type: str # "new", "review", "complete", "error"
    message: str
    topic_id: int | None = None
    topic_name: str | None = None
    project_title: str | None = None

class QuizOptionResponse(BaseModel):
    key: str
    label: str


class QuizQuestionResponse(BaseModel):
    id: int
    prompt: str
    explanation: str | None = None
    options: list[QuizOptionResponse]


class QuizPayload(BaseModel):
    topic_id: int
    topic_name: str | None = None
    question_count: int
    questions: list[QuizQuestionResponse]


class QuizSubmission(BaseModel):
    topic_id: int
    answers: dict[str, str] # e.g., {"12": "A", "14": "C"}

class TopicContentResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    content: str | None = None
    module_name: str | None = None
    related_projects: list[str] = []
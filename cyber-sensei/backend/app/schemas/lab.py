from pydantic import BaseModel


class LabModuleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class LabTopicResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class LabInstructionResponse(BaseModel):
    lab_id: str
    title: str
    objective: str
    steps: list[str]
    expected_duration: str | None = None


class LabCommandRequest(BaseModel):
    command: str


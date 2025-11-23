from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    skill_level: str = "beginner"
    learning_style: str = "mixed"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models
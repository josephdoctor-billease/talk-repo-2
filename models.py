from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    completed: bool = Field(False, description="Task completion status")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    completed: Optional[bool] = Field(None, description="Task completion status")


class Task(TaskBase):
    id: int = Field(..., description="Unique task identifier")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete FastAPI tutorial",
                "description": "Learn how to build REST APIs with FastAPI",
                "completed": False
            }
        }
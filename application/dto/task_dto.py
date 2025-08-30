from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )


class TaskUpdateDTO(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponseDTO(BaseModel):
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Task update timestamp")


class TaskListResponseDTO(BaseModel):
    tasks: List[TaskResponseDTO] = Field(..., description="List of tasks")
    total_count: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")

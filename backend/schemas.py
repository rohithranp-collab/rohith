from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SubtaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskResponse(SubtaskBase):
    id: int
    todo_id: int
    is_completed: int
    created_at: str


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""
    category: str = Field(default="Personal")
    priority: str = Field(default="medium")
    due_date: Optional[str] = None
    subtasks: Optional[List[str]] = []


class TodoUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""
    category: str = Field(default="Personal")
    priority: str = Field(default="medium")
    due_date: Optional[str] = None
    status: str = Field(default="pending")


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    category: str
    priority: str
    status: str
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
    subtasks: List[SubtaskResponse] = []


class DashboardStats(BaseModel):
    total: int
    completed: int
    pending: int
    high_priority: int
    completion_rate: int
    categories: Dict[str, int]

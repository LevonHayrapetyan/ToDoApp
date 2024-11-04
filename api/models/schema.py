from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr, Field

class CreateUser(BaseModel):
    username: EmailStr 
    password: str = Field(min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str


class TaskPriority(Enum):
    low = "low"
    medium = "medium"
    high = "high"

class AddToDo(BaseModel):
    name: str
    description:Optional[str] = Field(None, min_length=5)
    priority: TaskPriority 
    deadline: Optional[datetime] = None


class EmailSchema(BaseModel):
    email: List[EmailStr]








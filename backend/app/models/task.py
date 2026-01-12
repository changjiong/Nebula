import uuid
from datetime import datetime
from typing import Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON

# Shared properties
class TaskBase(SQLModel):
    name: str = Field(max_length=255)
    total_items: int = Field(default=0)

# Properties to receive on creation
class TaskCreate(TaskBase):
    pass

# Properties to receive on update
class TaskUpdate(SQLModel):
    status: str | None = None
    processed_items: int | None = None
    result: dict | None = None
    error_log: dict | None = None

# Database model
class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: str = Field(default="pending", max_length=50)
    processed_items: int = Field(default=0)
    
    # Use sa_column for JSON storage
    error_log: dict | None = Field(default=None, sa_column=Column(JSON))
    result: dict | None = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = Field(default=None)

# Properties to return via API
class TaskPublic(TaskBase):
    id: uuid.UUID
    status: str
    processed_items: int
    error_log: dict | None
    result: dict | None
    created_at: datetime
    finished_at: datetime | None

class TasksPublic(SQLModel):
    data: list[TaskPublic]
    count: int

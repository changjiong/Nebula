import uuid
from typing import Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from datetime import datetime

# Shared properties
class AgentBase(SQLModel):
    name: str = Field(index=True, max_length=255)
    description: str | None = Field(default=None)
    system_prompt: str = Field(default="")
    model_name: str = Field(default="gpt-4", max_length=255)
    temperature: float = Field(default=0.7)
    is_active: bool = Field(default=True)
    # Use sa_column for JSON storage of tools configuration
    tools: list[str] | None = Field(default=None, sa_column=Column(JSON))

# Properties to receive on creation
class AgentCreate(AgentBase):
    pass

# Properties to receive on update
class AgentUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    system_prompt: str | None = Field(default=None)
    model_name: str | None = Field(default=None, max_length=255)
    temperature: float | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    tools: list[str] | None = Field(default=None)

# Database model
class Agent(AgentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

# Properties to return via API
class AgentPublic(AgentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class AgentsPublic(SQLModel):
    data: list[AgentPublic]
    count: int

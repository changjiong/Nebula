import uuid
from datetime import datetime

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


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

    # Category for grouping (e.g., "entity_resolution", "risk_evaluation")
    category: str = Field(default="default", max_length=100)

    # Permission configuration (per implementation_plan.md section 10)
    # visibility: "public" = all users, "department" = filtered by department, "role" = filtered by role
    visibility: str = Field(default="public", max_length=20)
    # List of department names that can access this agent (only if visibility="department")
    allowed_departments: list[str] | None = Field(default=None, sa_column=Column(JSON))
    # List of role names that can access this agent (only if visibility="role")
    allowed_roles: list[str] | None = Field(default=None, sa_column=Column(JSON))

    # Execution mode: "realtime" for SSE, "batch" for async tasks
    execution_mode: str = Field(default="realtime", max_length=20)


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
    category: str | None = Field(default=None, max_length=100)
    visibility: str | None = Field(default=None, max_length=20)
    allowed_departments: list[str] | None = Field(default=None)
    allowed_roles: list[str] | None = Field(default=None)
    execution_mode: str | None = Field(default=None, max_length=20)


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


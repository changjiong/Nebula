"""
Tool Model - Atomic callable unit for Native Function Calling

Each Tool represents a single capability that can be invoked by the LLM,
such as an ML model, data API, or external service.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlmodel import Column, Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB


# ============ Tool Types ============

ToolType = Literal["ml_model", "data_api", "external_api", "builtin"]
VisibilityType = Literal["public", "department", "role"]
ToolStatus = Literal["draft", "active", "deprecated"]


# ============ Base Schema ============

class ToolBase(SQLModel):
    """Shared properties for Tool"""
    name: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Unique identifier for the tool (e.g., kechuang_score)"
    )
    display_name: str = Field(
        max_length=200,
        description="Human-readable display name"
    )
    description: str = Field(
        max_length=2000,
        description="Detailed description for LLM understanding"
    )
    
    # Type and configuration
    tool_type: str = Field(
        default="builtin",
        max_length=50,
        description="Type: ml_model, data_api, external_api, builtin"
    )
    service_config: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Service-specific configuration (endpoint, model_id, etc.)"
    )
    
    # Function Calling Schema (core for Native FC)
    input_schema: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="JSON Schema for input parameters"
    )
    output_schema: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="JSON Schema for output structure"
    )
    examples: list[dict] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Example input/output pairs for LLM"
    )
    
    # Metadata
    version: str = Field(default="1.0.0", max_length=20)
    status: str = Field(default="active", max_length=20)
    category: str = Field(default="general", max_length=100)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB)
    )
    
    # Permission control
    visibility: str = Field(
        default="public",
        max_length=20,
        description="Visibility: public, department, role"
    )
    allowed_departments: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Departments allowed to use this tool"
    )
    allowed_roles: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Roles allowed to use this tool"
    )


# ============ Database Model ============

class Tool(ToolBase, table=True):
    """Tool database model"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Statistics
    call_count: int = Field(default=0)
    avg_latency_ms: float = Field(default=0.0)
    success_rate: float = Field(default=1.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID | None = Field(default=None, foreign_key="user.id")


# ============ API Schemas ============

class ToolCreate(ToolBase):
    """Schema for creating a new tool"""
    pass


class ToolUpdate(SQLModel):
    """Schema for updating a tool (all fields optional)"""
    name: str | None = Field(default=None, max_length=100)
    display_name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    tool_type: str | None = Field(default=None, max_length=50)
    service_config: dict | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    examples: list[dict] | None = None
    version: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, max_length=20)
    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    visibility: str | None = Field(default=None, max_length=20)
    allowed_departments: list[str] | None = None
    allowed_roles: list[str] | None = None


class ToolPublic(ToolBase):
    """Schema for public tool response"""
    id: uuid.UUID
    call_count: int
    avg_latency_ms: float
    success_rate: float
    created_at: datetime
    updated_at: datetime


class ToolsPublic(SQLModel):
    """Schema for paginated tools list"""
    data: list[ToolPublic]
    count: int


class ToolTestRequest(SQLModel):
    """Schema for testing a tool"""
    params: dict = Field(description="Input parameters for the tool")


class ToolTestResult(SQLModel):
    """Schema for tool test result"""
    success: bool
    result: dict | None = None
    error: str | None = None
    latency_ms: float


class ToolForLLM(SQLModel):
    """Schema for tool definition sent to LLM (Function Calling format)"""
    name: str
    description: str
    input_schema: dict
    
    @classmethod
    def from_tool(cls, tool: Tool) -> "ToolForLLM":
        """Convert Tool to LLM-friendly format"""
        return cls(
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema
        )

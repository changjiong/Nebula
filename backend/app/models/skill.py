"""
Skill Model - DAG orchestration of multiple Tools

A Skill combines multiple Tools into a workflow (DAG), allowing complex
business logic to be composed from atomic tool capabilities.
"""

import uuid
from datetime import datetime
from typing import Literal

from sqlmodel import Column, Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB


# ============ Types ============

SkillStatus = Literal["draft", "active", "deprecated"]
VisibilityType = Literal["public", "department", "role"]


# ============ Base Schema ============

class SkillBase(SQLModel):
    """Shared properties for Skill"""
    name: str = Field(
        index=True,
        unique=True,
        max_length=100,
        description="Unique identifier for the skill"
    )
    display_name: str = Field(
        max_length=200,
        description="Human-readable display name"
    )
    description: str = Field(
        max_length=2000,
        description="Detailed description of what the skill does"
    )
    
    # DAG Workflow definition
    workflow: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="DAG workflow definition with nodes and edges"
    )
    # Example workflow structure:
    # {
    #   "nodes": [
    #     {"id": "step1", "tool": "enterprise_query", "params_mapping": {"query": "$.input.company_name"}},
    #     {"id": "step2", "tool": "kechuang_score", "depends_on": ["step1"], "params_mapping": {"credit_code": "$.step1.credit_code"}}
    #   ],
    #   "output_mapping": {"enterprise": "$.step1", "score": "$.step2"}
    # }
    
    # Associated tool IDs
    tool_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="List of tool IDs used in this skill"
    )
    
    # Input/Output schema (aggregated from tools or manually defined)
    input_schema: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="JSON Schema for skill input"
    )
    output_schema: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="JSON Schema for skill output"
    )
    
    # Metadata
    version: str = Field(default="1.0.0", max_length=20)
    status: str = Field(default="active", max_length=20)
    category: str = Field(default="general", max_length=100)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB)
    )
    
    # Permission control (can inherit from tools or override)
    visibility: str = Field(
        default="public",
        max_length=20,
        description="Visibility: public, department, role"
    )
    allowed_departments: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB)
    )
    allowed_roles: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB)
    )


# ============ Database Model ============

class Skill(SkillBase, table=True):
    """Skill database model"""
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

class SkillCreate(SkillBase):
    """Schema for creating a new skill"""
    pass


class SkillUpdate(SQLModel):
    """Schema for updating a skill (all fields optional)"""
    name: str | None = Field(default=None, max_length=100)
    display_name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    workflow: dict | None = None
    tool_ids: list[str] | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    version: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, max_length=20)
    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    visibility: str | None = Field(default=None, max_length=20)
    allowed_departments: list[str] | None = None
    allowed_roles: list[str] | None = None


class SkillPublic(SkillBase):
    """Schema for public skill response"""
    id: uuid.UUID
    call_count: int
    avg_latency_ms: float
    success_rate: float
    created_at: datetime
    updated_at: datetime


class SkillsPublic(SQLModel):
    """Schema for paginated skills list"""
    data: list[SkillPublic]
    count: int


class SkillTestRequest(SQLModel):
    """Schema for testing a skill"""
    params: dict = Field(description="Input parameters for the skill")


class SkillTestResult(SQLModel):
    """Schema for skill test result"""
    success: bool
    result: dict | None = None
    error: str | None = None
    latency_ms: float
    tool_results: dict | None = Field(
        default=None,
        description="Individual results from each tool in the workflow"
    )


# ============ Workflow Node Schema ============

class WorkflowNode(SQLModel):
    """Schema for a node in the skill workflow DAG"""
    id: str = Field(description="Unique node identifier within the workflow")
    tool: str = Field(description="Tool name to execute at this node")
    depends_on: list[str] = Field(
        default_factory=list,
        description="List of node IDs this node depends on"
    )
    params_mapping: dict = Field(
        default_factory=dict,
        description="JSONPath mapping from previous results to tool params"
    )
    condition: str | None = Field(
        default=None,
        description="Optional condition expression for conditional execution"
    )

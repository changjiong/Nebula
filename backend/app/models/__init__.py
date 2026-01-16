import uuid

from pydantic import EmailStr
from sqlalchemy import JSON, text
from sqlmodel import Field, Relationship, SQLModel

from .agent import Agent, AgentCreate, AgentPublic, AgentsPublic, AgentUpdate
from .conversation import (
    Conversation,
    ConversationCreate,
    ConversationPublic,
    ConversationsPublic,
    ConversationUpdate,
    ConversationWithMessages,
    MessageCreate,
    MessagePublic,
)
from .conversation import (
    Message as ChatMessage,
)
from .model_provider import (
    PRESET_PROVIDERS,
    ModelProvider,
    ModelProviderCreate,
    ModelProviderPublic,
    ModelProvidersPublic,
    ModelProviderTestResult,
    ModelProviderUpdate,
)
from .skill import (
    Skill,
    SkillCreate,
    SkillPublic,
    SkillsPublic,
    SkillTestRequest,
    SkillTestResult,
    SkillUpdate,
    WorkflowNode,
)
from .task import Task, TaskCreate, TaskPublic, TasksPublic, TaskUpdate
from .tool import (
    Tool,
    ToolCreate,
    ToolForLLM,
    ToolPublic,
    ToolsPublic,
    ToolTestRequest,
    ToolTestResult,
    ToolUpdate,
)
from .standard_table import StandardTable, TableField, ToolDataMapping


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=500)
    # Permission control fields
    department: str | None = Field(default=None, max_length=100, description="用户所属部门")
    roles: list[str] = Field(default=[], sa_type=JSON, sa_column_kwargs={"server_default": text("'[]'")}, description="用户角色列表")


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=500)
    department: str | None = Field(default=None, max_length=100)
    roles: list[str] | None = None


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Note: Item model has been removed as part of code cleanup.
# Legacy Item-related code should be migrated to use Tool/Skill models.


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


__all__ = [
    # User
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserUpdateMe",
    "UserRegister",
    "UserPublic",
    "UsersPublic",
    "UpdatePassword",
    # Auth
    "Message",
    "Token",
    "TokenPayload",
    "NewPassword",
    # Agent
    "Agent",
    "AgentCreate",
    "AgentUpdate",
    "AgentPublic",
    "AgentsPublic",
    # Conversation
    "Conversation",
    "ConversationCreate",
    "ConversationPublic",
    "ConversationsPublic",
    "ConversationUpdate",
    "ConversationWithMessages",
    "ChatMessage",
    "MessageCreate",
    "MessagePublic",
    # Task
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskPublic",
    "TasksPublic",
    # ModelProvider
    "PRESET_PROVIDERS",
    "ModelProvider",
    "ModelProviderCreate",
    "ModelProviderUpdate",
    "ModelProviderPublic",
    "ModelProvidersPublic",
    "ModelProviderTestResult",
    # Tool (NEW)
    "Tool",
    "ToolCreate",
    "ToolUpdate",
    "ToolPublic",
    "ToolsPublic",
    "ToolTestRequest",
    "ToolTestResult",
    "ToolForLLM",
    # Skill (NEW)
    "Skill",
    "SkillCreate",
    "SkillUpdate",
    "SkillPublic",
    "SkillsPublic",
    "SkillTestRequest",
    "SkillTestResult",
    "WorkflowNode",
    # Standard Table (NEW)
    "StandardTable",
    "TableField",
    "ToolDataMapping",
]

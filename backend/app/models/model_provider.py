"""Model Provider models for managing AI service providers."""

import uuid
from datetime import datetime

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


# ============================================================================
# 预置服务商模板
# ============================================================================
PRESET_PROVIDERS = [
    {
        "name": "OpenAI",
        "provider_type": "openai",
        "api_url": "https://api.openai.com/v1",
        "icon": "openai",
        "default_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    {
        "name": "DeepSeek",
        "provider_type": "deepseek",
        "api_url": "https://api.deepseek.com/v1",
        "icon": "deepseek",
        "default_models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
    },
    {
        "name": "Google Gemini",
        "provider_type": "gemini",
        "api_url": "https://generativelanguage.googleapis.com/v1beta",
        "icon": "gemini",
        "default_models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    },
    {
        "name": "阿里通义千问",
        "provider_type": "qwen",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "icon": "qwen",
        "default_models": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"],
    },
    {
        "name": "Anthropic Claude",
        "provider_type": "anthropic",
        "api_url": "https://api.anthropic.com/v1",
        "icon": "anthropic",
        "default_models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
    },
    {
        "name": "月之暗面 Kimi",
        "provider_type": "moonshot",
        "api_url": "https://api.moonshot.cn/v1",
        "icon": "moonshot",
        "default_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    },
    {
        "name": "智谱 GLM",
        "provider_type": "zhipu",
        "api_url": "https://open.bigmodel.cn/api/paas/v4",
        "icon": "zhipu",
        "default_models": ["glm-4-plus", "glm-4-flash", "glm-4-long"],
    },
    {
        "name": "百度文心一言",
        "provider_type": "baidu",
        "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
        "icon": "baidu",
        "default_models": ["ernie-4.0-8k", "ernie-3.5-8k", "ernie-speed-8k"],
    },
]


# ============================================================================
# 数据库模型
# ============================================================================
class ModelProviderBase(SQLModel):
    """Shared properties for ModelProvider."""

    name: str = Field(max_length=100, index=True)
    provider_type: str = Field(max_length=50)
    api_url: str = Field(max_length=500)
    api_key: str = Field(default="", max_length=500)
    is_enabled: bool = Field(default=True)
    icon: str | None = Field(default=None, max_length=100)
    models: list[str] = Field(default=[], sa_type=JSON)


class ModelProvider(ModelProviderBase, table=True):
    """Database model for AI model providers."""

    __tablename__ = "model_provider"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# API Schema
# ============================================================================
class ModelProviderCreate(SQLModel):
    """Schema for creating a model provider."""

    name: str = Field(max_length=100)
    provider_type: str = Field(max_length=50)
    api_url: str = Field(max_length=500)
    api_key: str = Field(default="", max_length=500)
    is_enabled: bool = Field(default=True)
    icon: str | None = Field(default=None, max_length=100)
    models: list[str] = Field(default=[])


class ModelProviderUpdate(SQLModel):
    """Schema for updating a model provider."""

    name: str | None = Field(default=None, max_length=100)
    provider_type: str | None = Field(default=None, max_length=50)
    api_url: str | None = Field(default=None, max_length=500)
    api_key: str | None = Field(default=None, max_length=500)
    is_enabled: bool | None = None
    icon: str | None = Field(default=None, max_length=100)
    models: list[str] | None = None


class ModelProviderPublic(SQLModel):
    """Schema for public model provider data (masks api_key)."""

    id: uuid.UUID
    name: str
    provider_type: str
    api_url: str
    api_key_set: bool  # 只显示是否已设置，不暴露实际密钥
    is_enabled: bool
    icon: str | None
    models: list[str]
    created_at: datetime
    updated_at: datetime


class ModelProvidersPublic(SQLModel):
    """Schema for paginated list of model providers."""

    data: list[ModelProviderPublic]
    count: int


class ModelProviderTestResult(SQLModel):
    """Schema for API connection test result."""

    success: bool
    message: str
    available_models: list[str] = []

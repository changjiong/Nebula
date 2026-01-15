"""Model Provider API routes."""

import uuid
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    PRESET_PROVIDERS,
    ModelProvider,
    ModelProviderCreate,
    ModelProviderPublic,
    ModelProvidersPublic,
    ModelProviderTestResult,
    ModelProviderUpdate,
)

router = APIRouter()


def _provider_to_public(provider: ModelProvider) -> ModelProviderPublic:
    """Convert ModelProvider to ModelProviderPublic (masks api_key)."""
    return ModelProviderPublic(
        id=provider.id,
        name=provider.name,
        provider_type=provider.provider_type,
        api_url=provider.api_url,
        api_key_set=bool(provider.api_key),
        is_enabled=provider.is_enabled,
        icon=provider.icon,
        models=provider.models,
        created_at=provider.created_at,
        updated_at=provider.updated_at,
    )


@router.get("/", response_model=ModelProvidersPublic)
def get_model_providers(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """获取当前用户的所有模型服务商。"""
    count_statement = (
        select(func.count())
        .select_from(ModelProvider)
        .where(ModelProvider.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(ModelProvider)
        .where(ModelProvider.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(ModelProvider.created_at)
    )
    providers = session.exec(statement).all()

    return ModelProvidersPublic(
        data=[_provider_to_public(p) for p in providers],
        count=count,
    )


@router.get("/presets")
def get_preset_providers() -> list[dict]:
    """获取预置的服务商模板列表。"""
    return PRESET_PROVIDERS


@router.post("/", response_model=ModelProviderPublic)
def create_model_provider(
    session: SessionDep,
    current_user: CurrentUser,
    provider_in: ModelProviderCreate,
) -> Any:
    """创建新的模型服务商。"""
    # Check if provider with same name already exists
    existing = session.exec(
        select(ModelProvider)
        .where(ModelProvider.owner_id == current_user.id)
        .where(ModelProvider.name == provider_in.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Provider with name '{provider_in.name}' already exists",
        )

    provider = ModelProvider(
        **provider_in.model_dump(),
        owner_id=current_user.id,
    )
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return _provider_to_public(provider)


@router.post("/init-presets", response_model=ModelProvidersPublic)
def initialize_preset_providers(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """为用户初始化预置服务商（仅首次使用时调用）。"""
    # Check if user already has providers
    existing_count = session.exec(
        select(func.count())
        .select_from(ModelProvider)
        .where(ModelProvider.owner_id == current_user.id)
    ).one()

    if existing_count > 0:
        # User already has providers, just return them
        statement = select(ModelProvider).where(ModelProvider.owner_id == current_user.id)
        providers = session.exec(statement).all()
        return ModelProvidersPublic(
            data=[_provider_to_public(p) for p in providers],
            count=existing_count,
        )

    # Create preset providers for the user
    created_providers = []
    for preset in PRESET_PROVIDERS:
        provider = ModelProvider(
            name=preset["name"],
            provider_type=preset["provider_type"],
            api_url=preset["api_url"],
            api_key="",  # User needs to fill in
            is_enabled=False,  # Disabled by default until configured
            icon=preset["icon"],
            models=preset["default_models"],
            owner_id=current_user.id,
        )
        session.add(provider)
        created_providers.append(provider)

    session.commit()
    for p in created_providers:
        session.refresh(p)

    return ModelProvidersPublic(
        data=[_provider_to_public(p) for p in created_providers],
        count=len(created_providers),
    )


@router.get("/{provider_id}", response_model=ModelProviderPublic)
def get_model_provider(
    session: SessionDep,
    current_user: CurrentUser,
    provider_id: uuid.UUID,
) -> Any:
    """获取单个模型服务商详情。"""
    provider = session.get(ModelProvider, provider_id)
    if not provider or provider.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Provider not found")
    return _provider_to_public(provider)


@router.put("/{provider_id}", response_model=ModelProviderPublic)
def update_model_provider(
    session: SessionDep,
    current_user: CurrentUser,
    provider_id: uuid.UUID,
    provider_in: ModelProviderUpdate,
) -> Any:
    """更新模型服务商配置。"""
    provider = session.get(ModelProvider, provider_id)
    if not provider or provider.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Provider not found")

    update_data = provider_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    from datetime import datetime

    provider.updated_at = datetime.utcnow()

    session.add(provider)
    session.commit()
    session.refresh(provider)
    return _provider_to_public(provider)


@router.delete("/{provider_id}")
def delete_model_provider(
    session: SessionDep,
    current_user: CurrentUser,
    provider_id: uuid.UUID,
) -> dict:
    """删除模型服务商。"""
    provider = session.get(ModelProvider, provider_id)
    if not provider or provider.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Provider not found")

    session.delete(provider)
    session.commit()
    return {"message": "Provider deleted successfully"}


@router.post("/{provider_id}/test", response_model=ModelProviderTestResult)
async def test_provider_connection(
    session: SessionDep,
    current_user: CurrentUser,
    provider_id: uuid.UUID,
) -> Any:
    """测试模型服务商 API 连接。"""
    provider = session.get(ModelProvider, provider_id)
    if not provider or provider.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Provider not found")

    if not provider.api_key:
        return ModelProviderTestResult(
            success=False,
            message="API key not configured",
            available_models=[],
        )

    try:
        # Test connection based on provider type
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider.provider_type in ("openai", "deepseek", "moonshot", "qwen"):
                # OpenAI-compatible API
                response = await client.get(
                    f"{provider.api_url}/models",
                    headers={"Authorization": f"Bearer {provider.api_key}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    return ModelProviderTestResult(
                        success=True,
                        message="Connection successful",
                        available_models=models[:20],  # Limit to 20 models
                    )
                else:
                    return ModelProviderTestResult(
                        success=False,
                        message=f"API error: {response.status_code}",
                        available_models=[],
                    )

            elif provider.provider_type == "anthropic":
                # Anthropic doesn't have a models endpoint, just verify the key
                response = await client.get(
                    f"{provider.api_url}/messages",
                    headers={
                        "x-api-key": provider.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                # A 400 error (missing body) still means the key is valid
                if response.status_code in (200, 400):
                    return ModelProviderTestResult(
                        success=True,
                        message="API key is valid",
                        available_models=provider.models,
                    )
                return ModelProviderTestResult(
                    success=False,
                    message=f"API error: {response.status_code}",
                    available_models=[],
                )

            elif provider.provider_type == "gemini":
                # Google Gemini
                response = await client.get(
                    f"{provider.api_url}/models?key={provider.api_key}",
                )
                if response.status_code == 200:
                    data = response.json()
                    models = [
                        m.get("name", "").replace("models/", "")
                        for m in data.get("models", [])
                    ]
                    return ModelProviderTestResult(
                        success=True,
                        message="Connection successful",
                        available_models=models[:20],
                    )
                return ModelProviderTestResult(
                    success=False,
                    message=f"API error: {response.status_code}",
                    available_models=[],
                )

            else:
                # For other providers, just return success with stored models
                return ModelProviderTestResult(
                    success=True,
                    message="Configuration saved (connection not tested)",
                    available_models=provider.models,
                )

    except httpx.TimeoutException:
        return ModelProviderTestResult(
            success=False,
            message="Connection timeout",
            available_models=[],
        )
    except Exception as e:
        return ModelProviderTestResult(
            success=False,
            message=f"Connection error: {str(e)}",
            available_models=[],
        )


@router.get("/{provider_id}/models")
async def get_provider_models(
    session: SessionDep,
    current_user: CurrentUser,
    provider_id: uuid.UUID,
) -> list[str]:
    """获取服务商可用的模型列表。"""
    provider = session.get(ModelProvider, provider_id)
    if not provider or provider.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Provider not found")

    # If we have stored models, return them
    if provider.models:
        return provider.models

    # Otherwise, try to fetch from API
    if not provider.api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider.provider_type in ("openai", "deepseek", "moonshot", "qwen"):
                response = await client.get(
                    f"{provider.api_url}/models",
                    headers={"Authorization": f"Bearer {provider.api_key}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    return [m.get("id") for m in data.get("data", [])][:20]
    except Exception:
        pass

    return provider.models or []

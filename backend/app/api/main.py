from fastapi import APIRouter

from app.api.routes import (
    agents,
    avatar,
    chat,
    login,
    model_providers,
    private,
    skills,
    standard_tables,
    tasks,
    tools,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(avatar.router)  # Avatar upload endpoints
api_router.include_router(utils.router)
# Business routers
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    model_providers.router, prefix="/model-providers", tags=["model-providers"]
)
# Knowledge engineering routers (NEW)
api_router.include_router(tools.router)  # /tools - Tool management
api_router.include_router(skills.router)  # /skills - Skill management
api_router.include_router(standard_tables.router, tags=["standard-tables"])  # /standard-tables


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)


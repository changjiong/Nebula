from fastapi import APIRouter

from app.api.routes import agents, chat, login, private, tasks, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
# New routers
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

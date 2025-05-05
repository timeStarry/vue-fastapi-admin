from fastapi import APIRouter

from .notification import router

notification_router = APIRouter()
notification_router.include_router(router, tags=["通知模块"])

__all__ = ["notification_router"]
 
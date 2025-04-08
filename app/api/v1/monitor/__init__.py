from fastapi import APIRouter

from .host import router as host_router

monitor_router = APIRouter()
monitor_router.include_router(host_router, prefix="/host", tags=["主机监控"])

__all__ = ["monitor_router"]

from fastapi import APIRouter

from .tickets import router as tickets_router

tickets_router = APIRouter()
tickets_router.include_router(tickets_router, prefix="/host", tags=["主机监控"])

__all__ = ["monitor_router"]

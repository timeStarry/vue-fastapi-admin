from fastapi import APIRouter


from .tickets import router

tickets_router = APIRouter()
tickets_router.include_router(router, tags=["工单管理"])

__all__ = ["tickets_router"] 

from .tickets import router as tickets_router

tickets_router = APIRouter()
tickets_router.include_router(tickets_router, prefix="/host", tags=["主机监控"])

__all__ = ["monitor_router"]


from fastapi import APIRouter

from .tickets import router

tickets_router = APIRouter()
tickets_router.include_router(router, tags=["工单模块"])

__all__ = ["tickets_router"]

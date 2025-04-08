from fastapi import APIRouter

#from .monitor import router

base_router = APIRouter()
#base_router.include_router(router, tags=["监控模块"])

__all__ = ["base_router"]

from fastapi import APIRouter

from .agno import router

agno_router = APIRouter()
agno_router.include_router(router, tags=["agno模块"])

__all__ = ["agno_router"]

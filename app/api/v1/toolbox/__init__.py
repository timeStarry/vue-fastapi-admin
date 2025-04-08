from fastapi import APIRouter

# 如果 toolbox.py 中没有特殊的路由，可以移除这行
# from .toolbox import router  
from .network import router as network_router
from .system import router as system_router
from .security import router as security_router

toolbox_router = APIRouter()
# 如果没有特殊路由，可以移除这行
# toolbox_router.include_router(router, tags=["工具箱"])
toolbox_router.include_router(network_router, tags=["网络工具"])
toolbox_router.include_router(system_router, tags=["系统工具"])
toolbox_router.include_router(security_router, tags=["安全工具"])

__all__ = ["toolbox_router"]

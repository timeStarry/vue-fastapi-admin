from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, permissions, menus, monitor
from app.api.v1.toolbox import toolbox

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限"])
api_router.include_router(menus.router, prefix="/menus", tags=["菜单"])
#api_router.include_router(monitor.router, prefix="/monitor", tags=["监控"])
api_router.include_router(toolbox.router, prefix="/toolbox", tags=["工具箱"]) 
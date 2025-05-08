from fastapi import APIRouter

from app.core.dependency import DependPermisson

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router
from .tickets import tickets_router
from .monitor import monitor_router
from .notification import notification_router
from .agno import router as agno_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermisson])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermisson])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermisson])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermisson])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermisson])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermisson])
v1_router.include_router(tickets_router, prefix="/ticket", dependencies=[DependPermisson])
v1_router.include_router(monitor_router, prefix="/monitor", dependencies=[DependPermisson])
v1_router.include_router(notification_router, prefix="/notification", dependencies=[DependPermisson])
v1_router.include_router(agno_router, prefix="/agno", dependencies=[DependPermisson])

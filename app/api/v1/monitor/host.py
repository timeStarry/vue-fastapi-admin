from fastapi import APIRouter, Query, Depends
from tortoise.expressions import Q

from app.controllers.monitor import host_group_controller, monitor_host_controller
from app.schemas.monitor import HostGroupCreate, HostGroupUpdate, MonitorHostCreate, MonitorHostUpdate
from app.schemas import Success, SuccessExtra
from app.core.dependency import AuthControl
from app.models.admin import User

router = APIRouter()

# 主机分组相关接口
@router.get("/groups", summary="获取主机分组列表", tags=["主机监控"])
async def get_host_groups(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query(None, description="分组名称"),
):
    total, data = await host_group_controller.get_list(page=page, page_size=page_size, name=name)
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.get("/group", summary="获取主机分组详情", tags=["主机监控"])
async def get_host_group(
    group_id: int = Query(..., description="分组ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    group = await host_group_controller.get(id=group_id)
    data = await group.to_dict()
    return Success(data=data)

@router.post("/group/create", summary="创建主机分组", tags=["主机监控"])
async def create_host_group(
    group: HostGroupCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await host_group_controller.create(group)
    return Success(msg="创建成功")

@router.put("/group/{group_id}", summary="更新主机分组", tags=["主机监控"])
async def update_host_group(
    group_id: int,
    group: HostGroupUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await host_group_controller.update(group_id, group)
    return Success(msg="更新成功")

@router.delete("/group/{group_id}", summary="删除主机分组", tags=["主机监控"])
async def delete_host_group(
    group_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    await host_group_controller.delete(group_id)
    return Success(msg="删除成功")

@router.post("/group/{group_id}/set-default", summary="设置默认分组", tags=["主机监控"])
async def set_default_group(
    group_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    await host_group_controller.set_default(group_id)
    return Success(msg="设置成功")

# 主机管理相关接口
@router.get("/list", summary="获取主机列表", tags=["主机监控"])
async def get_monitor_hosts(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="主机名称"),
    ip: str = Query("", description="IP地址"),
    group_id: int = Query(None, description="分组ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    query = {}
    if name:
        query["name__icontains"] = name
    if ip:
        query["ip__icontains"] = ip
    if group_id:
        query["group_id"] = group_id
    
    result = await monitor_host_controller.get_list(page, page_size, **query)
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/create", summary="创建主机", tags=["主机监控"])
async def create_monitor_host(
    host: MonitorHostCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await monitor_host_controller.create(host)
    return Success(msg="创建成功")

@router.put("/{host_id}", summary="更新主机", tags=["主机监控"])
async def update_monitor_host(
    host_id: int,
    host: MonitorHostUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await monitor_host_controller.update(host_id, host)
    return Success(msg="更新成功")

@router.delete("/{host_id}", summary="删除主机", tags=["主机监控"])
async def delete_monitor_host(
    host_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    await monitor_host_controller.remove(id=host_id)
    return Success(msg="删除成功")

@router.post("/test-connection", summary="测试主机连接", tags=["主机监控"])
async def test_host_connection(
    host_data: dict,
    current_user: User = Depends(AuthControl.is_authed)
):
    result = await monitor_host_controller.test_connection(host_data)
    return Success(data=result) 
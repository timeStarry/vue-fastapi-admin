from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.monitor import (
    HostCreate, HostUpdate, PingTestResult,
    ServiceCreate, ServiceUpdate, ServiceTestResult,
    DashboardData, AlertUpdate
)
from app.controllers.monitor import MonitorController
from app.core.dependency import AuthControl
from app.schemas.base import Success, SuccessExtra

router = APIRouter()

# 主机监控相关接口
@router.get("/host", summary="获取主机列表")
async def get_host_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    host_name: Optional[str] = Query(None, description="主机名"),
    ip: Optional[str] = Query(None, description="IP地址"),
    status: Optional[str] = Query(None, description="状态"),
    host_type: Optional[str] = Query(None, description="主机类型"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取主机列表"""
    result = await MonitorController.get_host_list(
        page=page,
        page_size=page_size,
        host_name=host_name,
        ip=ip,
        status=status,
        host_type=host_type
    )
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/host", summary="创建主机")
async def create_host(
    host_data: HostCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建主机"""
    host = await MonitorController.create_host(host_data)
    if not host:
        raise HTTPException(status_code=400, detail="创建主机失败")
    return Success(data=host)

@router.get("/host/{host_id}", summary="获取主机详情")
async def get_host(
    host_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取主机详情"""
    host = await MonitorController.get_host(host_id)
    if not host:
        raise HTTPException(status_code=404, detail="主机不存在")
    return Success(data=host)

@router.put("/host/{host_id}", summary="更新主机")
async def update_host(
    host_id: int,
    host_data: HostUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新主机"""
    host = await MonitorController.update_host(host_id, host_data)
    if not host:
        raise HTTPException(status_code=404, detail="主机不存在")
    return Success(data=host)

@router.delete("/host/{host_id}", summary="删除主机")
async def delete_host(
    host_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除主机"""
    success = await MonitorController.delete_host(host_id)
    if not success:
        raise HTTPException(status_code=404, detail="主机不存在")
    return Success(msg="删除成功")

@router.post("/host/{host_id}/ping", summary="Ping测试主机")
async def ping_host(
    host_id: int,
    current_user = Depends(AuthControl.is_authed)
) -> PingTestResult:
    """Ping测试主机"""
    result = await MonitorController.ping_host(host_id)
    if not result.success and "主机不存在" in result.message:
        raise HTTPException(status_code=404, detail="主机不存在")
    return Success(data=result.dict())

@router.get("/host/{host_id}/mrtg", summary="获取MRTG数据")
async def get_mrtg_data(
    host_id: int,
    days: int = Query(1, ge=1, le=30, description="天数"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取MRTG数据"""
    data = await MonitorController.get_mrtg_data(host_id, days)
    return Success(data={"items": data})

@router.post("/host/{host_id}/mrtg/mock", summary="生成模拟MRTG数据")
async def generate_mock_mrtg_data(
    host_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """生成模拟的MRTG数据（仅用于演示）"""
    data = await MonitorController.generate_mock_mrtg_data(host_id)
    if not data:
        raise HTTPException(status_code=400, detail="生成MRTG数据失败")
    return Success(data=data)


# 服务监控相关接口
@router.get("/service", summary="获取服务列表")
async def get_service_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    service_name: Optional[str] = Query(None, description="服务名称"),
    url: Optional[str] = Query(None, description="服务URL"),
    status: Optional[str] = Query(None, description="状态"),
    service_type: Optional[str] = Query(None, description="服务类型"),
    host_id: Optional[int] = Query(None, description="主机ID"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取服务列表"""
    result = await MonitorController.get_service_list(
        page=page,
        page_size=page_size,
        service_name=service_name,
        url=url,
        status=status,
        service_type=service_type,
        host_id=host_id
    )
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/service", summary="创建服务")
async def create_service(
    service_data: ServiceCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建服务"""
    service = await MonitorController.create_service(service_data)
    if not service:
        raise HTTPException(status_code=400, detail="创建服务失败")
    return Success(data=service)

@router.get("/service/{service_id}", summary="获取服务详情")
async def get_service(
    service_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取服务详情"""
    service = await MonitorController.get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    return Success(data=service)

@router.put("/service/{service_id}", summary="更新服务")
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新服务"""
    service = await MonitorController.update_service(service_id, service_data)
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    return Success(data=service)

@router.delete("/service/{service_id}", summary="删除服务")
async def delete_service(
    service_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除服务"""
    success = await MonitorController.delete_service(service_id)
    if not success:
        raise HTTPException(status_code=404, detail="服务不存在")
    return Success(msg="删除成功")

@router.post("/service/{service_id}/check", summary="检测服务")
async def check_service(
    service_id: int,
    current_user = Depends(AuthControl.is_authed)
) -> ServiceTestResult:
    """检测服务"""
    result = await MonitorController.check_service(service_id)
    if not result.success and "服务不存在" in result.message:
        raise HTTPException(status_code=404, detail="服务不存在")
    return Success(data=result.dict())

@router.get("/service/{service_id}/history", summary="获取服务响应时间历史")
async def get_service_history(
    service_id: int,
    days: int = Query(1, ge=1, le=30, description="天数"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取服务响应时间历史"""
    data = await MonitorController.get_service_history(service_id, days)
    return Success(data={"items": data})


# 监控面板相关接口
@router.get("/dashboard", summary="获取监控面板数据")
async def get_dashboard_data(
    current_user = Depends(AuthControl.is_authed)
):
    """获取监控面板数据"""
    data = await MonitorController.get_dashboard_data()
    # 将DashboardData对象转换为字典以便正确序列化
    return Success(data=data.dict())


# 告警相关接口
@router.get("/alert", summary="获取告警列表")
async def get_alert_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    level: Optional[str] = Query(None, description="级别"),
    target_type: Optional[str] = Query(None, description="目标类型"),
    resolved: Optional[bool] = Query(None, description="是否已解决"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取告警列表"""
    result = await MonitorController.get_alert_list(
        page=page,
        page_size=page_size,
        level=level,
        target_type=target_type,
        resolved=resolved
    )
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.get("/alert/{alert_id}", summary="获取告警详情")
async def get_alert(
    alert_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取告警详情"""
    alert = await MonitorController.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")
    return Success(data=alert)

@router.put("/alert/{alert_id}", summary="更新告警")
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新告警"""
    alert = await MonitorController.update_alert(alert_id, alert_data)
    if not alert:
        raise HTTPException(status_code=404, detail="告警不存在")
    return Success(data=alert) 
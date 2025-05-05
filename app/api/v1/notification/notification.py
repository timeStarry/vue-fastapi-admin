from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependency import AuthControl
from app.schemas.base import Success, SuccessExtra

from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, ChannelCreate, ChannelUpdate,
    TemplateCreate, TemplateUpdate, SettingCreate, SettingUpdate,
    NotificationFromTemplate, QueueStatus, NotificationPriority, ChannelType
)
from app.controllers.notification import NotificationController

router = APIRouter()

# 通知队列API
@router.get("/queue", summary="获取通知队列列表")
async def get_queue_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    source: Optional[str] = Query(None, description="消息来源"),
    status: Optional[QueueStatus] = Query(None, description="处理状态"),
    priority: Optional[NotificationPriority] = Query(None, description="优先级"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知队列列表"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_queue_list(page, page_size, source, status, priority)
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/queue", summary="创建通知")
async def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建通知"""
    # 仅管理员可创建，权限由AuthControl控制
    result = await NotificationController.create_notification(notification_data)
    return Success(data=result)

@router.post("/queue/from-template", summary="根据模板创建通知")
async def create_notification_from_template(
    data: NotificationFromTemplate,
    current_user = Depends(AuthControl.is_authed)
):
    """根据模板创建通知"""
    # 仅管理员可创建，权限由AuthControl控制
    result = await NotificationController.create_notification_from_template(data)
    return Success(data=result)

@router.get("/queue/{notification_id}", summary="获取通知详情")
async def get_notification(
    notification_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知详情"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_notification(notification_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知不存在")
    return Success(data=result)

@router.put("/queue/{notification_id}", summary="更新通知")
async def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新通知"""
    # 仅管理员可更新，权限由AuthControl控制
    result = await NotificationController.update_notification(notification_id, notification_data)
    if not result:
        raise HTTPException(status_code=404, detail="通知不存在")
    return Success(data=result)

@router.delete("/queue/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除通知"""
    # 仅管理员可删除，权限由AuthControl控制
    result = await NotificationController.delete_notification(notification_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知不存在")
    return Success(data={"success": True})

# 通知渠道API
@router.get("/channel", summary="获取通知渠道列表")
async def get_channel_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    channel_type: Optional[ChannelType] = Query(None, description="渠道类型"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知渠道列表"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_channel_list(page, page_size, channel_type, is_active)
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/channel/test", summary="测试通知渠道连接")
async def test_channel(
    channel_data: ChannelCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """测试通知渠道连接"""
    # 仅管理员可测试，权限由AuthControl控制
    try:
        result = await NotificationController.test_channel(channel_data)
        return Success(data=result, msg="连接测试成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"测试连接失败: {str(e)}")

@router.post("/channel", summary="创建通知渠道")
async def create_channel(
    channel_data: ChannelCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建通知渠道"""
    # 仅管理员可创建，权限由AuthControl控制
    result = await NotificationController.create_channel(channel_data)
    return Success(data=result)

@router.get("/channel/{channel_id}", summary="获取通知渠道详情")
async def get_channel(
    channel_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知渠道详情"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_channel(channel_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知渠道不存在")
    return Success(data=result)

@router.put("/channel/{channel_id}", summary="更新通知渠道")
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新通知渠道"""
    # 仅管理员可更新，权限由AuthControl控制
    result = await NotificationController.update_channel(channel_id, channel_data)
    if not result:
        raise HTTPException(status_code=404, detail="通知渠道不存在")
    return Success(data=result)

@router.delete("/channel/{channel_id}", summary="删除通知渠道")
async def delete_channel(
    channel_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除通知渠道"""
    # 仅管理员可删除，权限由AuthControl控制
    result = await NotificationController.delete_channel(channel_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知渠道不存在")
    return Success(data={"success": True})

# 通知模板API
@router.get("/template", summary="获取通知模板列表")
async def get_template_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知模板列表"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_template_list(page, page_size, is_active)
    return SuccessExtra(
        data=result["items"], 
        total=result["total"], 
        page=result["page"], 
        page_size=result["page_size"]
    )

@router.post("/template", summary="创建通知模板")
async def create_template(
    template_data: TemplateCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建通知模板"""
    # 仅管理员可创建，权限由AuthControl控制
    try:
        result = await NotificationController.create_template(template_data)
        return Success(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/template/{template_id}", summary="获取通知模板详情")
async def get_template(
    template_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取通知模板详情"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知模板不存在")
    return Success(data=result)

@router.get("/template/key/{template_key}", summary="根据键名获取通知模板")
async def get_template_by_key(
    template_key: str,
    current_user = Depends(AuthControl.is_authed)
):
    """根据键名获取通知模板"""
    # 仅管理员可查看，权限由AuthControl控制
    result = await NotificationController.get_template_by_key(template_key)
    if not result:
        raise HTTPException(status_code=404, detail="通知模板不存在")
    return Success(data=result)

@router.put("/template/{template_id}", summary="更新通知模板")
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user = Depends(AuthControl.is_authed)
):
    """更新通知模板"""
    # 仅管理员可更新，权限由AuthControl控制
    result = await NotificationController.update_template(template_id, template_data)
    if not result:
        raise HTTPException(status_code=404, detail="通知模板不存在")
    return Success(data=result)

@router.delete("/template/{template_id}", summary="删除通知模板")
async def delete_template(
    template_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除通知模板"""
    # 仅管理员可删除，权限由AuthControl控制
    result = await NotificationController.delete_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知模板不存在")
    return Success(data={"success": True})

# 用户通知设置API - 这些API需要用户身份信息
@router.get("/setting/user/{user_id}", summary="获取用户通知设置")
async def get_user_settings(
    user_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """获取用户通知设置"""
    # 检查权限：只能查看自己的设置或管理员可查看所有
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限查看其他用户的通知设置")
    
    result = await NotificationController.get_user_settings(user_id)
    return Success(data=result)

@router.get("/setting/user/{user_id}/source/{source}", summary="获取用户特定来源的通知设置")
async def get_user_source_setting(
    user_id: int,
    source: str,
    current_user = Depends(AuthControl.is_authed)
):
    """获取用户特定来源的通知设置"""
    # 检查权限：只能查看自己的设置或管理员可查看所有
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限查看其他用户的通知设置")
    
    result = await NotificationController.get_user_source_setting(user_id, source)
    if not result:
        # 如果不存在，返回默认设置
        return Success(data={
            "user_id": user_id,
            "source": source,
            "enabled_channels": [],
            "is_enabled": True
        })
    return Success(data=result)

@router.post("/setting", summary="创建或更新通知设置")
async def create_or_update_setting(
    setting_data: SettingCreate,
    current_user = Depends(AuthControl.is_authed)
):
    """创建或更新通知设置"""
    # 检查权限：只能修改自己的设置或管理员可修改所有
    if current_user.id != setting_data.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限修改其他用户的通知设置")
    
    result = await NotificationController.create_or_update_setting(setting_data)
    return Success(data=result)

@router.delete("/setting/{setting_id}", summary="删除通知设置")
async def delete_setting(
    setting_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """删除通知设置"""
    # 仅管理员可删除，权限由AuthControl控制
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限删除通知设置")
        
    result = await NotificationController.delete_setting(setting_id)
    if not result:
        raise HTTPException(status_code=404, detail="通知设置不存在")
    return Success(data={"success": True})

# 集成API
@router.post("/monitor-alert/{alert_id}", summary="将监控告警添加到通知队列")
async def add_monitor_alert_to_queue(
    alert_id: int,
    current_user = Depends(AuthControl.is_authed)
):
    """将监控告警添加到通知队列"""
    # 仅管理员可操作，权限由AuthControl控制
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
        
    try:
        result = await NotificationController.add_monitor_alert_to_queue(alert_id)
        return Success(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/ticket-status-change/{ticket_id}", summary="将工单状态变更添加到通知队列")
async def add_ticket_status_change_to_queue(
    ticket_id: int,
    old_status: str,
    new_status: str,
    current_user = Depends(AuthControl.is_authed)
):
    """将工单状态变更添加到通知队列"""
    # 仅管理员可操作，权限由AuthControl控制
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
        
    try:
        result = await NotificationController.add_ticket_status_change_to_queue(ticket_id, old_status, new_status)
        return Success(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
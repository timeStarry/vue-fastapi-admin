from fastapi import APIRouter, Depends
from app.controllers.notification import NotificationController
from app.core.dependency import DependAuth
from app.core.ctx import CTX_USER_ID
router = APIRouter()
notification_ctl = NotificationController()

@router.get("/list", summary="获取当前用户的通知列表", dependencies=[DependAuth])
async def get_notifications():
    """获取当前用户的通知列表"""
    user_id = CTX_USER_ID.get()
    return await notification_ctl.get_user_notifications(user_id)

@router.post("/read/{notification_id}", summary="标记通知为已读", dependencies=[DependAuth])
async def mark_notification_read(notification_id: int):
    """标记通知为已读"""
    return await notification_ctl.mark_as_read(notification_id) 
from app.core.crud import CRUDBase
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate

class NotificationController(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    def __init__(self):
        super().__init__(model=Notification)
    
    async def create_notification(self, user_id: int, title: str, content: str, type: str = "info"):
        """创建新通知"""
        return await self.create({
            "user_id": user_id,
            "title": title,
            "content": content,
            "type": type
        })
    
    async def get_user_notifications(self, user_id: int, is_read: bool = None):
        """获取用户通知列表"""
        query = {"user_id": user_id}
        if is_read is not None:
            query["is_read"] = is_read
        return await self.model.filter(**query).order_by("-created_at")
    
    async def mark_as_read(self, notification_id: int):
        """标记通知为已读"""
        notification = await self.get(notification_id)
        if notification:
            await notification.update_from_dict({"is_read": True}).save() 
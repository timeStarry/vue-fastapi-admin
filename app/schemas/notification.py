from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    content: str
    type: str = "info"
    is_read: bool = False
    user_id: int

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 
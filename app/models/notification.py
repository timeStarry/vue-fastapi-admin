from tortoise import fields

from .base import BaseModel, TimestampMixin

class Notification(BaseModel, TimestampMixin):
    """通知模型"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200, description="通知标题")
    content = fields.TextField(description="通知内容")
    type = fields.CharField(max_length=20, description="通知类型", default="info")  # info, warning, error, success
    is_read = fields.BooleanField(default=False, description="是否已读")
    user_id = fields.IntField(description="接收用户ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
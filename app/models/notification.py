from tortoise import fields
from enum import Enum
from typing import Dict, Any, Optional
import datetime

from app.models.base import BaseModel, TimestampMixin

class QueueStatus(str, Enum):
    """队列状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 处理完成
    FAILED = "failed"  # 处理失败

class NotificationPriority(str, Enum):
    """通知优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    EMAIL = "email"
    SMS = "sms"
    WECHAT = "wechat"
    WEBHOOK = "webhook"
    SYSTEM = "system"  # 系统内部通知

class NotificationQueue(BaseModel, TimestampMixin):
    """通知队列模型"""
    source = fields.CharField(max_length=50, description="消息来源", index=True)  # monitor, ticket, system, etc.
    source_id = fields.IntField(description="来源ID", null=True, index=True)
    title = fields.CharField(max_length=200, description="通知标题")
    content = fields.TextField(description="通知内容")
    priority = fields.CharEnumField(NotificationPriority, description="优先级", default=NotificationPriority.NORMAL, index=True)
    status = fields.CharEnumField(QueueStatus, description="处理状态", default=QueueStatus.PENDING, index=True)
    scheduled_at = fields.DatetimeField(description="计划发送时间", null=True, index=True)
    processed_at = fields.DatetimeField(description="处理时间", null=True, index=True)
    retry_count = fields.IntField(description="重试次数", default=0)
    max_retries = fields.IntField(description="最大重试次数", default=3)
    data = fields.JSONField(description="附加数据", null=True)
    
    class Meta:
        table = "notification_queue"
        table_description = "通知队列表"

    def __str__(self):
        return f"{self.source}:{self.title}"

    async def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "scheduled_at": self.scheduled_at.strftime("%Y-%m-%d %H:%M:%S") if self.scheduled_at else None,
            "processed_at": self.processed_at.strftime("%Y-%m-%d %H:%M:%S") if self.processed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "data": self.data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

class NotificationChannel(BaseModel, TimestampMixin):
    """通知渠道模型"""
    name = fields.CharField(max_length=100, description="渠道名称")
    channel_type = fields.CharEnumField(NotificationChannel, description="渠道类型", index=True)
    config = fields.JSONField(description="渠道配置")
    is_active = fields.BooleanField(description="是否启用", default=True, index=True)
    
    class Meta:
        table = "notification_channel"
        table_description = "通知渠道表"

    def __str__(self):
        return f"{self.name} ({self.channel_type})"

    async def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "channel_type": self.channel_type,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

class NotificationTemplate(BaseModel, TimestampMixin):
    """通知模板模型"""
    name = fields.CharField(max_length=100, description="模板名称", index=True)
    template_key = fields.CharField(max_length=100, description="模板键名", unique=True, index=True)
    title_template = fields.TextField(description="标题模板")
    content_template = fields.TextField(description="内容模板")
    applicable_channels = fields.JSONField(description="适用渠道", default=list)
    is_active = fields.BooleanField(description="是否启用", default=True, index=True)
    
    class Meta:
        table = "notification_template"
        table_description = "通知模板表"

    def __str__(self):
        return f"{self.name} ({self.template_key})"

    async def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "template_key": self.template_key,
            "title_template": self.title_template,
            "content_template": self.content_template,
            "applicable_channels": self.applicable_channels,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

class NotificationLog(BaseModel, TimestampMixin):
    """通知发送日志模型"""
    queue = fields.ForeignKeyField('models.NotificationQueue', related_name='logs', on_delete=fields.CASCADE)
    channel = fields.ForeignKeyField('models.NotificationChannel', related_name='logs', on_delete=fields.SET_NULL, null=True)
    channel_name = fields.CharField(max_length=100, description="渠道名称")
    channel_type = fields.CharField(max_length=50, description="渠道类型", index=True)
    recipients = fields.JSONField(description="接收者", default=list)
    status = fields.CharField(max_length=20, description="发送状态", index=True)  # success, failed
    error_message = fields.TextField(description="错误信息", null=True)
    response_data = fields.JSONField(description="响应数据", null=True)
    
    class Meta:
        table = "notification_log"
        table_description = "通知发送日志表"

    def __str__(self):
        return f"{self.channel_name} - {self.status}"

    async def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "queue_id": self.queue_id,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "channel_type": self.channel_type,
            "recipients": self.recipients,
            "status": self.status,
            "error_message": self.error_message,
            "response_data": self.response_data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }

class NotificationSetting(BaseModel, TimestampMixin):
    """通知设置模型"""
    user_id = fields.IntField(description="用户ID", index=True)
    source = fields.CharField(max_length=50, description="消息来源", index=True)  # monitor, ticket, system, etc.
    enabled_channels = fields.JSONField(description="启用的渠道", default=list)  # 例如: ["email", "wechat"]
    is_enabled = fields.BooleanField(description="是否启用", default=True, index=True)
    
    class Meta:
        table = "notification_setting"
        table_description = "通知设置表"
        unique_together = (("user_id", "source"),)

    def __str__(self):
        return f"User {self.user_id} - {self.source}"

    async def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source": self.source,
            "enabled_channels": self.enabled_channels,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        } 
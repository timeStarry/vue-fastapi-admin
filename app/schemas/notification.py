from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

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

class ChannelType(str, Enum):
    """通知渠道枚举"""
    EMAIL = "email"
    SMS = "sms"
    WECHAT = "wechat"
    WEBHOOK = "webhook"
    SYSTEM = "system"  # 系统内部通知

class NotificationCreate(BaseModel):
    """创建通知请求"""
    source: str = Field(..., description="消息来源", example="monitor")
    source_id: Optional[int] = Field(None, description="来源ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="优先级")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")
    max_retries: Optional[int] = Field(3, description="最大重试次数")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")

class NotificationUpdate(BaseModel):
    """更新通知请求"""
    title: Optional[str] = Field(None, description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    priority: Optional[NotificationPriority] = Field(None, description="优先级")
    status: Optional[QueueStatus] = Field(None, description="处理状态")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")
    max_retries: Optional[int] = Field(None, description="最大重试次数")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")

class ChannelCreate(BaseModel):
    """创建通知渠道请求"""
    name: str = Field(..., description="渠道名称")
    channel_type: ChannelType = Field(..., description="渠道类型")
    config: Dict[str, Any] = Field(..., description="渠道配置")
    is_active: bool = Field(True, description="是否启用")

class ChannelUpdate(BaseModel):
    """更新通知渠道请求"""
    name: Optional[str] = Field(None, description="渠道名称")
    config: Optional[Dict[str, Any]] = Field(None, description="渠道配置")
    is_active: Optional[bool] = Field(None, description="是否启用")

class TemplateCreate(BaseModel):
    """创建通知模板请求"""
    name: str = Field(..., description="模板名称")
    template_key: str = Field(..., description="模板键名")
    title_template: str = Field(..., description="标题模板")
    content_template: str = Field(..., description="内容模板")
    applicable_channels: List[str] = Field([], description="适用渠道")
    is_active: bool = Field(True, description="是否启用")

class TemplateUpdate(BaseModel):
    """更新通知模板请求"""
    name: Optional[str] = Field(None, description="模板名称")
    title_template: Optional[str] = Field(None, description="标题模板")
    content_template: Optional[str] = Field(None, description="内容模板")
    applicable_channels: Optional[List[str]] = Field(None, description="适用渠道")
    is_active: Optional[bool] = Field(None, description="是否启用")

class SettingCreate(BaseModel):
    """创建通知设置请求"""
    user_id: int = Field(..., description="用户ID")
    source: str = Field(..., description="消息来源")
    enabled_channels: List[str] = Field([], description="启用的渠道")
    is_enabled: bool = Field(True, description="是否启用")

class SettingUpdate(BaseModel):
    """更新通知设置请求"""
    enabled_channels: Optional[List[str]] = Field(None, description="启用的渠道")
    is_enabled: Optional[bool] = Field(None, description="是否启用")

class NotificationQueueResponse(BaseModel):
    """通知队列响应"""
    id: int
    source: str
    source_id: Optional[int]
    title: str
    content: str
    priority: str
    status: str
    scheduled_at: Optional[str]
    processed_at: Optional[str]
    retry_count: int
    max_retries: int
    data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str

class ChannelResponse(BaseModel):
    """通知渠道响应"""
    id: int
    name: str
    channel_type: str
    config: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str

class TemplateResponse(BaseModel):
    """通知模板响应"""
    id: int
    name: str
    template_key: str
    title_template: str
    content_template: str
    applicable_channels: List[str]
    is_active: bool
    created_at: str
    updated_at: str

class LogResponse(BaseModel):
    """通知日志响应"""
    id: int
    queue_id: int
    channel_id: Optional[int]
    channel_name: str
    channel_type: str
    recipients: List[Any]
    status: str
    error_message: Optional[str]
    response_data: Optional[Dict[str, Any]]
    created_at: str

class SettingResponse(BaseModel):
    """通知设置响应"""
    id: int
    user_id: int
    source: str
    enabled_channels: List[str]
    is_enabled: bool
    created_at: str
    updated_at: str

class NotificationFromTemplate(BaseModel):
    """根据模板创建通知"""
    template_key: str = Field(..., description="模板键名")
    source: str = Field(..., description="消息来源", example="monitor")
    source_id: Optional[int] = Field(None, description="来源ID")
    template_data: Dict[str, Any] = Field({}, description="模板数据")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="优先级")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")
    max_retries: Optional[int] = Field(3, description="最大重试次数")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="附加数据") 
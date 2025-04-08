from enum import Enum
from tortoise import fields

from .base import BaseModel, TimestampMixin

class TicketStatus(str, Enum):
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    CLOSED = "closed"      # 已关闭

class TicketPriority(str, Enum):
    LOW = "low"      # 低优先级
    MEDIUM = "medium"  # 中优先级
    HIGH = "high"    # 高优先级

class TicketType(str, Enum):
    REPAIR = "repair"        # 故障报修
    SUGGESTION = "suggestion"  # 需求建议
    QUESTION = "question"    # 咨询问题

class Ticket(BaseModel, TimestampMixin):
    title = fields.CharField(max_length=200, description="工单标题")
    content = fields.JSONField(description="工单内容")
    type = fields.CharEnumField(TicketType, description="工单类型")
    priority = fields.CharEnumField(TicketPriority, default=TicketPriority.MEDIUM, description="优先级")
    status = fields.CharEnumField(TicketStatus, default=TicketStatus.PENDING, description="工单状态")
    
    creator_id = fields.IntField(description="创建人ID")
    creator_name = fields.CharField(max_length=64, description="创建人姓名")
    assignee_id = fields.IntField(null=True, description="受理人ID")
    assignee_name = fields.CharField(max_length=64, null=True, description="受理人姓名")
    dept_id = fields.IntField(description="所属部门ID")
    
    class Meta:
        table = "ticket"

class TicketComment(BaseModel, TimestampMixin):
    ticket_id = fields.IntField(description="工单ID")
    content = fields.JSONField(description="评论内容")
    user_id = fields.IntField(description="评论人ID")
    username = fields.CharField(max_length=64, description="评论人姓名")
    
    class Meta:
        table = "ticket_comment"

class TicketLog(BaseModel, TimestampMixin):
    ticket_id = fields.IntField(description="工单ID")
    action = fields.CharField(max_length=32, description="操作类型")
    content = fields.JSONField(description="操作内容")
    operator_id = fields.IntField(description="操作人ID")
    operator_name = fields.CharField(max_length=64, description="操作人姓名")
    
    class Meta:
        table = "ticket_log" 
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.base import BaseModel, TimestampMixin
from app.models.admin import User


class Ticket(BaseModel, TimestampMixin):
    """工单模型"""
    ticket_no = fields.CharField(max_length=50, description="工单编号", unique=True, index=True)
    title = fields.CharField(max_length=200, description="工单标题", index=True)
    description = fields.TextField(description="工单描述")
    type = fields.CharField(max_length=50, description="工单类型", index=True)
    status = fields.CharField(max_length=50, description="工单状态", default="pending", index=True)
    priority = fields.CharField(max_length=50, description="优先级", default="medium", index=True)
    creator = fields.ForeignKeyField("models.User", related_name="created_tickets", description="创建人", index=True)
    assignee = fields.ForeignKeyField("models.User", related_name="assigned_tickets", description="处理人", null=True, index=True)
    expected_time = fields.DatetimeField(description="期望完成时间", null=True, index=True)
    finished_time = fields.DatetimeField(description="实际完成时间", null=True, index=True)

    class Meta:
        table = "ticket"
        table_description = "工单表"

    def __str__(self):
        return self.title

    async def to_dict(self, include_process_records=False):
        creator_obj = await self.creator
        assignee_obj = await self.assignee if self.assignee_id else None
        
        # 获取处理记录
        process_records = []
        if include_process_records:
            record_objs = await TicketRecord.filter(ticket_id=self.id).order_by("created_at").prefetch_related("operator")
            for record in record_objs:
                operator = await record.operator
                record_dict = {
                    "id": record.id,
                    "action": record.action,
                    "action_name": record.get_action_name(),
                    "content": record.content,
                    "operator_id": operator.id,
                    "operator_name": operator.username,
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "attachments": [] # 这里需要实现附件获取
                }
                process_records.append(record_dict)
        
        return {
            "id": self.id,
            "ticket_no": self.ticket_no,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "creator_id": creator_obj.id,
            "creator_name": creator_obj.username,
            "assignee_id": assignee_obj.id if assignee_obj else None,
            "assignee_name": assignee_obj.username if assignee_obj else None,
            "expected_time": self.expected_time.strftime("%Y-%m-%d %H:%M:%S") if self.expected_time else None,
            "finished_time": self.finished_time.strftime("%Y-%m-%d %H:%M:%S") if self.finished_time else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "process_records": process_records if include_process_records else [],
        }


class TicketRecord(BaseModel, TimestampMixin):
    """工单处理记录"""
    ticket = fields.ForeignKeyField("models.Ticket", related_name="records", description="工单", index=True)
    action = fields.CharField(max_length=50, description="操作类型", index=True)
    content = fields.TextField(description="处理内容")
    operator = fields.ForeignKeyField("models.User", related_name="ticket_operations", description="操作人", index=True)

    class Meta:
        table = "ticket_record"
        table_description = "工单处理记录表"

    def __str__(self):
        return f"{self.ticket.ticket_no} - {self.action}"
    
    def get_action_name(self):
        """获取操作类型名称"""
        action_names = {
            "create": "创建工单",
            "accept": "接单",
            "process": "处理",
            "complete": "完成",
            "confirm": "确认",
            "reject": "退回",
            "transfer": "转派",
            "close": "关闭",
            "reopen": "重新打开",
        }
        return action_names.get(self.action, self.action)


class TicketAttachment(BaseModel, TimestampMixin):
    """工单附件"""
    ticket = fields.ForeignKeyField("models.Ticket", related_name="attachments", description="工单", null=True, index=True)
    record = fields.ForeignKeyField("models.TicketRecord", related_name="attachments", description="工单记录", null=True, index=True)
    file_name = fields.CharField(max_length=255, description="文件名", index=True)
    file_path = fields.CharField(max_length=255, description="文件路径", index=True)
    file_size = fields.IntField(description="文件大小(字节)", index=True)
    file_type = fields.CharField(max_length=50, description="文件类型", index=True)
    uploader = fields.ForeignKeyField("models.User", related_name="uploaded_files", description="上传人", index=True)

    class Meta:
        table = "ticket_attachment"
        table_description = "工单附件表"

    def __str__(self):
        return self.file_name
    
    async def to_dict(self):
        uploader_obj = await self.uploader
        base_url = "/api/v1/ticket/files/"  # 这里需要替换为实际的文件访问路径
        
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "uploader_id": uploader_obj.id,
            "uploader_name": uploader_obj.username,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "url": f"{base_url}{self.file_path}"
        } 
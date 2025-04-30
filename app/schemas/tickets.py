from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TicketBase(BaseModel):
    """工单基本信息"""
    title: str = Field(..., description="工单标题")
    description: str = Field(..., description="工单描述")
    type: str = Field(..., description="工单类型", example="fault")
    priority: str = Field("medium", description="优先级", example="medium")


class TicketCreate(TicketBase):
    """创建工单请求"""
    assignee_id: Optional[int] = Field(None, description="处理人ID")
    expected_time: Optional[datetime] = Field(None, description="期望完成时间")


class TicketUpdate(BaseModel):
    """更新工单请求"""
    title: Optional[str] = Field(None, description="工单标题")
    description: Optional[str] = Field(None, description="工单描述")
    type: Optional[str] = Field(None, description="工单类型")
    priority: Optional[str] = Field(None, description="优先级")
    assignee_id: Optional[int] = Field(None, description="处理人ID")
    expected_time: Optional[datetime] = Field(None, description="期望完成时间")


class TicketAttachmentResponse(BaseModel):
    """附件响应"""
    id: int
    file_name: str
    file_size: int
    file_type: str
    uploader_id: int
    uploader_name: str
    created_at: str
    url: str


class TicketRecordResponse(BaseModel):
    """工单处理记录响应"""
    id: int
    action: str
    action_name: str
    content: str
    operator_id: int
    operator_name: str
    created_at: str
    attachments: List[TicketAttachmentResponse] = []


class TicketResponse(BaseModel):
    """工单响应"""
    id: int
    ticket_no: str
    title: str
    description: str
    type: str
    status: str
    priority: str
    creator_id: int
    creator_name: str
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    expected_time: Optional[str] = None
    finished_time: Optional[str] = None
    created_at: str
    updated_at: str
    process_records: List[TicketRecordResponse] = []


class TicketProcess(BaseModel):
    """处理工单请求"""
    ticket_id: int = Field(..., description="工单ID")
    action: str = Field(..., description="处理动作", example="accept")
    content: str = Field(..., description="处理内容")
    assignee_id: Optional[int] = Field(None, description="转派目标ID (仅转派时使用)")
    attachments: Optional[List[int]] = Field([], description="附件ID列表")


class TicketStatisticsResponse(BaseModel):
    """工单统计响应"""
    overview: dict = Field(..., description="概览数据")
    type_distribution: List[dict] = Field(..., description="类型分布")
    status_distribution: List[dict] = Field(..., description="状态分布")
    priority_distribution: List[dict] = Field(..., description="优先级分布")
    trend_data: List[dict] = Field(..., description="趋势数据")
    process_time: List[dict] = Field(..., description="处理时长")
    assignee_workload: List[dict] = Field(..., description="处理人工作量")
    pending_tickets: List[dict] = Field(..., description="待处理工单") 
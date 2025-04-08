from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TicketBase(BaseModel):
    title: str = Field(..., description="工单标题", example="系统登录异常")
    content: dict = Field(..., description="工单内容", example={"type": "text", "content": "无法正常登录系统"})
    type: str = Field(..., description="工单类型")
    priority: str = Field("medium", description="优先级")
    dept_id: int = Field(..., description="所属部门ID")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    id: int = Field(..., description="工单ID")
    title: Optional[str] = Field(None, description="工单标题")
    content: Optional[dict] = Field(None, description="工单内容")
    type: Optional[str] = Field(None, description="工单类型")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="工单状态")
    assignee_id: Optional[int] = Field(None, description="受理人ID")

class TicketCommentCreate(BaseModel):
    ticket_id: int = Field(..., description="工单ID")
    content: dict = Field(..., description="评论内容") 
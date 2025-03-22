from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field

from app.models.ticket import TicketStatus, TicketPriority, TicketContentType


class TicketCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    desc: Optional[str] = Field(None, description="分类描述") 
    parent_id: int = Field(0, description="父分类ID")
    order: int = Field(0, description="排序")


class TicketCategoryCreate(TicketCategoryBase):
    pass


class TicketCategoryUpdate(TicketCategoryBase):
    id: int


class TicketContent(BaseModel):
    """工单内容基础结构"""
    type: TicketContentType
    data: Union[str, Dict[str, Any]]  # 根据type不同,data可以是字符串或字典


class TicketBase(BaseModel):
    title: str = Field(..., description="工单标题")
    content: TicketContent = Field(..., description="工单内容")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="优先级")
    category_id: int = Field(..., description="分类ID")
    dept_id: int = Field(..., description="部门ID")
    assignee_id: Optional[int] = Field(None, description="处理人ID")


class TicketCreate(TicketBase):
    pass


class TicketUpdate(TicketBase):
    id: int
    status: Optional[TicketStatus] = None


class TicketCommentCreate(BaseModel):
    ticket_id: int = Field(..., description="工单ID")
    content: str = Field(..., description="评论内容")


class TicketCommentOut(BaseModel):
    id: int
    content: str
    creator_name: str
    created_at: str 
from typing import List, Optional, Tuple
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.ticket import TicketCategory, Ticket, TicketComment, TicketContentType
from app.schemas.ticket import (
    TicketCategoryCreate, TicketCategoryUpdate,
    TicketCreate, TicketUpdate,
    TicketCommentCreate
)


class TicketCategoryController(CRUDBase[TicketCategory, TicketCategoryCreate, TicketCategoryUpdate]):
    def __init__(self):
        super().__init__(model=TicketCategory)

    async def get_category_tree(self, name: Optional[str] = None) -> List[dict]:
        """获取分类树"""
        query = Q()
        if name:
            query &= Q(name__contains=name)
            
        categories = await self.model.filter(query).order_by("order")
        
        def build_tree(parent_id: int = 0) -> List[dict]:
            return [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "desc": cat.desc,
                    "order": cat.order,
                    "parent_id": cat.parent_id,
                    "children": build_tree(cat.id)
                }
                for cat in categories
                if cat.parent_id == parent_id
            ]
            
        return build_tree()

class TicketController(CRUDBase[Ticket, TicketCreate, TicketUpdate]):
    def __init__(self):
        super().__init__(model=Ticket)
    
    async def create_ticket(self, obj_in: TicketCreate, user_id: int, username: str) -> Ticket:
        """创建工单"""
        ticket_dict = obj_in.model_dump()
        ticket_dict["creator_id"] = user_id
        ticket_dict["creator_name"] = username
        ticket_obj = await self.create(obj_in=ticket_dict)
        
        # 记录操作日志
        await TicketLog.create(
            ticket_id=ticket_obj.id,
            action="create",
            content="创建工单",
            operator_id=user_id,
            operator_name=username
        )
        return ticket_obj
    
    async def update_ticket(self, obj_in: TicketUpdate, user_id: int, username: str) -> Ticket:
        """更新工单"""
        ticket_obj = await self.get(id=obj_in.id)
        old_status = ticket_obj.status
        
        # 更新工单
        update_dict = obj_in.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(ticket_obj, field, value)
        await ticket_obj.save()
        
        # 记录状态变更
        if "status" in update_dict and update_dict["status"] != old_status:
            await TicketLog.create(
                ticket_id=ticket_obj.id,
                action="status_change",
                content=f"工单状态从 {old_status} 变更为 {update_dict['status']}",
                operator_id=user_id,
                operator_name=username
            )
        
        return ticket_obj 

    async def get_list(
        self, 
        page: int = 1,
        page_size: int = 10,
        **kwargs
    ) -> dict:
        """获取工单列表"""
        query = Q()
        if title := kwargs.get("title"):
            query &= Q(title__icontains=title)
        if status := kwargs.get("status"):
            query &= Q(status=status)
        if priority := kwargs.get("priority"):
            query &= Q(priority=priority)
        if category_id := kwargs.get("category_id"):
            query &= Q(category_id=category_id)
        if creator_id := kwargs.get("creator_id"):
            query &= Q(creator_id=creator_id)
        if assignee_id := kwargs.get("assignee_id"):
            query &= Q(assignee_id=assignee_id)
        if dept_id := kwargs.get("dept_id"):
            query &= Q(dept_id=dept_id)
            
        total, tickets = await self.list(page=page, page_size=page_size, search=query)
        
        items = []
        for ticket in tickets:
            ticket_dict = await ticket.to_dict()
            ticket_dict["creator_name"] = (await ticket.creator).name
            ticket_dict["assignee_name"] = (await ticket.assignee).name if ticket.assignee else None
            ticket_dict["category_name"] = (await ticket.category).name
            ticket_dict["dept_name"] = (await ticket.dept).name
            items.append(ticket_dict)
            
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def validate_content(self, content: dict) -> bool:
        """验证工单内容格式"""
        content_type = content.get("type")
        if not content_type or content_type not in TicketContentType:
            return False
            
        data = content.get("data")
        if content_type == TicketContentType.FORM:
            # 验证表单数据结构
            if not isinstance(data, dict):
                return False
            if "fields" not in data:
                return False
            # 可以添加更多的验证逻辑
            
        return True
    
    async def create(self, obj_in: TicketCreate) -> Ticket:
        """创建工单时验证内容格式"""
        if not await self.validate_content(obj_in.content.model_dump()):
            raise ValueError("Invalid ticket content format")
        return await super().create(obj_in)


class TicketCommentController:
    async def create_comment(self, obj_in: TicketCommentCreate, creator_id: int) -> TicketComment:
        """创建工单评论"""
        return await TicketComment.create(
            ticket_id=obj_in.ticket_id,
            content=obj_in.content,
            creator_id=creator_id
        )
        
    async def get_ticket_comments(self, ticket_id: int) -> List[dict]:
        """获取工单评论列表"""
        comments = await TicketComment.filter(ticket_id=ticket_id).order_by("-created_at")
        result = []
        for comment in comments:
            comment_dict = await comment.to_dict()
            comment_dict["creator_name"] = (await comment.creator).name
            result.append(comment_dict)
        return result


ticket_category_controller = TicketCategoryController()
ticket_controller = TicketController()
ticket_comment_controller = TicketCommentController() 
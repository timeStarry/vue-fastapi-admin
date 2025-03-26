from typing import List, Tuple
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.ticket import Ticket, TicketComment, TicketLog
from app.schemas.tickets import TicketCreate, TicketUpdate

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
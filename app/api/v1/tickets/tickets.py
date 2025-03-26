from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.ticket import TicketController
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.models.admin import User
from app.schemas.base import Success, SuccessExtra, Fail
from app.schemas.tickets import TicketCreate, TicketUpdate

router = APIRouter()
ticket_controller = TicketController()

@router.get("/list", summary="工单列表", dependencies=[DependAuth])
async def get_ticket_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    title: str = Query("", description="工单标题"),
    type: str = Query(None, description="工单类型"),
    status: str = Query(None, description="工单状态"),
    priority: str = Query(None, description="优先级"),
    dept_id: int = Query(None, description="部门ID"),
    start_time: str = Query("", description="开始时间"),
    end_time: str = Query("", description="结束时间"),
) -> SuccessExtra:
    """获取工单列表"""
    user_id = CTX_USER_ID.get()
    current_user = await User.get(id=user_id)
    
    q = Q()
    if title:
        q &= Q(title__icontains=title)
    if type:
        q &= Q(type=type)
    if status:
        q &= Q(status=status)
    if priority:
        q &= Q(priority=priority)
    if dept_id:
        q &= Q(dept_id=dept_id)
    if start_time and end_time:
        q &= Q(created_at__range=[start_time, end_time])
    
    # 如果不是管理员,只能看到自己部门的工单
    if not current_user.is_superuser:
        q &= Q(dept_id=current_user.dept_id)
    
    total, ticket_objs = await ticket_controller.list(
        page=page, 
        page_size=page_size,
        search=q,
        order=["-created_at"]  # 按创建时间倒序排序
    )
    data = [await ticket.to_dict() for ticket in ticket_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.get("/detail/{ticket_id}", summary="工单详情", dependencies=[DependAuth])
async def get_ticket_detail(ticket_id: int):
    """获取工单详情"""
    user_id = CTX_USER_ID.get()
    current_user = await User.get(id=user_id)
    
    ticket_obj = await ticket_controller.get(id=ticket_id)
    # 检查权限
    if not current_user.is_superuser and ticket_obj.dept_id != current_user.dept_id:
        return Fail(msg="无权限查看该工单")
    
    data = await ticket_obj.to_dict()
    return Success(data=data)

@router.post("/create", summary="创建工单", dependencies=[DependAuth])
async def create_ticket(ticket_in: TicketCreate):
    """创建工单"""
    user_id = CTX_USER_ID.get()
    current_user = await User.get(id=user_id)
    
    ticket_obj = await ticket_controller.create_ticket(
        obj_in=ticket_in,
        user_id=user_id,
        username=current_user.username
    )
    return Success(msg="工单创建成功")

@router.post("/update", summary="更新工单", dependencies=[DependAuth])
async def update_ticket(ticket_in: TicketUpdate):
    """更新工单"""
    user_id = CTX_USER_ID.get()
    current_user = await User.get(id=user_id)
    
    # 检查权限
    ticket_obj = await ticket_controller.get(id=ticket_in.id)
    if not current_user.is_superuser and ticket_obj.dept_id != current_user.dept_id:
        return Fail(msg="无权限更新该工单")
    
    await ticket_controller.update_ticket(
        obj_in=ticket_in,
        user_id=user_id,
        username=current_user.username
    )
    return Success(msg="工单更新成功")

@router.post("/close/{ticket_id}", summary="关闭工单", dependencies=[DependAuth])
async def close_ticket(ticket_id: int):
    """关闭工单"""
    user_id = CTX_USER_ID.get()
    current_user = await User.get(id=user_id)
    
    # 检查权限
    ticket_obj = await ticket_controller.get(id=ticket_id)
    if not current_user.is_superuser and ticket_obj.dept_id != current_user.dept_id:
        return Fail(msg="无权限关闭该工单")
    
    # 更新状态为已关闭
    await ticket_controller.update_ticket(
        obj_in=TicketUpdate(id=ticket_id, status="closed"),
        user_id=user_id,
        username=current_user.username
    )
    return Success(msg="工单已关闭") 
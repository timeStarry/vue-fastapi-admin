from fastapi import APIRouter, Query, Depends
from tortoise.expressions import Q

from app.controllers.ticket import ticket_controller, ticket_category_controller, ticket_comment_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, 
    TicketCategoryCreate, TicketCategoryUpdate,
    TicketCommentCreate
)
from app.core.dependency import AuthControl
from app.models.admin import User

router = APIRouter()

@router.get("/list", summary="获取工单列表")
async def get_ticket_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    title: str = Query("", description="工单标题"),
    status: str = Query("", description="工单状态"),
    priority: str = Query("", description="优先级"),
    category_id: int = Query(None, description="分类ID"),
    creator_id: int = Query(None, description="创建人ID"),
    assignee_id: int = Query(None, description="处理人ID"),
    dept_id: int = Query(None, description="部门ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    result = await ticket_controller.get_list(
        page=page,
        page_size=page_size,
        title=title,
        status=status,
        priority=priority,
        category_id=category_id,
        creator_id=creator_id,
        assignee_id=assignee_id,
        dept_id=dept_id
    )
    return SuccessExtra(**result)

@router.post("/create", summary="创建工单")
async def create_ticket(
    ticket_in: TicketCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    ticket_dict = ticket_in.model_dump()
    ticket_dict["creator_id"] = current_user.id
    ticket_dict["dept_id"] = current_user.dept_id
    await ticket_controller.create(obj_in=ticket_in)
    return Success(msg="Created Successfully")

@router.post("/update", summary="更新工单")
async def update_ticket(
    ticket_in: TicketUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_controller.update(obj_in=ticket_in)
    return Success(msg="Updated Successfully")

@router.delete("/delete", summary="删除工单")
async def delete_ticket(
    id: int = Query(..., description="工单ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_controller.delete(id=id)
    return Success(msg="Deleted Successfully")

# 工单分类相关接口
@router.get("/category/tree", summary="获取工单分类树")
async def get_category_tree(
    name: str = Query("", description="分类名称"),
    current_user: User = Depends(AuthControl.is_authed)
):
    result = await ticket_category_controller.get_category_tree(name=name)
    return Success(data=result)

@router.post("/category/create", summary="创建工单分类")
async def create_category(
    category_in: TicketCategoryCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_category_controller.create(obj_in=category_in)
    return Success(msg="Created Successfully")

@router.post("/category/update", summary="更新工单分类")
async def update_category(
    category_in: TicketCategoryUpdate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_category_controller.update(obj_in=category_in)
    return Success(msg="Updated Successfully")

@router.delete("/category/delete", summary="删除工单分类")
async def delete_category(
    id: int = Query(..., description="分类ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_category_controller.delete(id=id)
    return Success(msg="Deleted Successfully")

# 工单评论相关接口
@router.get("/comments", summary="获取工单评论")
async def get_ticket_comments(
    ticket_id: int = Query(..., description="工单ID"),
    current_user: User = Depends(AuthControl.is_authed)
):
    result = await ticket_comment_controller.get_ticket_comments(ticket_id=ticket_id)
    return Success(data=result)

@router.post("/comment/create", summary="创建工单评论")
async def create_comment(
    comment_in: TicketCommentCreate,
    current_user: User = Depends(AuthControl.is_authed)
):
    await ticket_comment_controller.create_comment(
        obj_in=comment_in,
        creator_id=current_user.id
    )
    return Success(msg="Created Successfully") 
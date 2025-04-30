import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, UploadFile, File, Form, Body, Depends
from tortoise.expressions import Q
from starlette.responses import FileResponse

from app.controllers.ticket import ticket_controller
from app.schemas import Success, SuccessExtra
from app.schemas.tickets import *
from app.settings.config import settings
from app.core.dependency import AuthControl

router = APIRouter()


@router.get("/list", summary="查看工单列表")
async def get_ticket_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    ticket_no: str = Query("", description="工单编号"),
    title: str = Query("", description="工单标题"),
    type: str = Query("", description="工单类型"),
    status: str = Query("", description="工单状态"),
    priority: str = Query("", description="优先级"),
    assignee_id: int = Query(None, description="处理人ID"),
    start_time: str = Query("", description="创建开始时间"),
    end_time: str = Query("", description="创建结束时间"),
    current_user = Depends(AuthControl.is_authed),
):
    """查询工单列表"""
    q = Q()
    
    if ticket_no:
        q &= Q(ticket_no__contains=ticket_no)
    if title:
        q &= Q(title__contains=title)
    if type:
        q &= Q(type=type)
    if status:
        q &= Q(status=status)
    if priority:
        q &= Q(priority=priority)
    if assignee_id:
        q &= Q(assignee_id=assignee_id)
    if start_time and end_time:
        q &= Q(created_at__range=[start_time, end_time])
    elif start_time:
        q &= Q(created_at__gte=start_time)
    elif end_time:
        q &= Q(created_at__lte=end_time)
    
    # 非管理员只能查看自己创建的或处理的工单
    if not current_user.is_superuser:
        q &= (Q(creator_id=current_user.id) | Q(assignee_id=current_user.id))
    
    total, ticket_objs = await ticket_controller.list(page=page, page_size=page_size, search=q)
    data = [await ticket.to_dict() for ticket in ticket_objs]
    
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="获取工单详情")
async def get_ticket(
    ticket_id: int = Query(..., description="工单ID"),
    current_user = Depends(AuthControl.is_authed),
):
    """获取工单详情"""
    ticket_obj = await ticket_controller.get(ticket_id)
    
    # 权限检查：只能查看自己创建的、处理的工单或管理员可查看所有
    if not current_user.is_superuser and current_user.id != ticket_obj.creator_id and current_user.id != ticket_obj.assignee_id:
        return Success(code=403, msg="无权限查看此工单")
    
    data = await ticket_obj.to_dict(include_process_records=True)
    return Success(data=data)


@router.post("/create", summary="创建工单")
async def create_ticket(
    ticket_in: TicketCreate,
    current_user = Depends(AuthControl.is_authed),
):
    """创建工单"""
    ticket_obj = await ticket_controller.create(
        title=ticket_in.title,
        description=ticket_in.description,
        type=ticket_in.type,
        priority=ticket_in.priority,
        creator_id=current_user.id,
        assignee_id=ticket_in.assignee_id,
        expected_time=ticket_in.expected_time,
    )
    
    return Success(msg="Created Successfully", data={"id": ticket_obj.id})


@router.post("/update", summary="更新工单")
async def update_ticket(
    ticket_id: int = Form(..., description="工单ID"),
    title: Optional[str] = Form(None, description="工单标题"),
    description: Optional[str] = Form(None, description="工单描述"),
    type: Optional[str] = Form(None, description="工单类型"),
    priority: Optional[str] = Form(None, description="优先级"),
    assignee_id: Optional[int] = Form(None, description="处理人ID"),
    expected_time: Optional[datetime] = Form(None, description="期望完成时间"),
    current_user = Depends(AuthControl.is_authed),
):
    """更新工单信息"""
    # 构建更新数据
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if type is not None:
        update_data["type"] = type
    if priority is not None:
        update_data["priority"] = priority
    if assignee_id is not None:
        update_data["assignee_id"] = assignee_id
    if expected_time is not None:
        update_data["expected_time"] = expected_time
    
    await ticket_controller.update(id=ticket_id, operator_id=current_user.id, data=update_data)
    
    return Success(msg="Updated Successfully")


@router.post("/process", summary="处理工单")
async def process_ticket(
    ticket_in: TicketProcess,
    current_user = Depends(AuthControl.is_authed),
):
    """处理工单"""
    await ticket_controller.process(
        ticket_id=ticket_in.ticket_id,
        operator_id=current_user.id,
        action=ticket_in.action,
        content=ticket_in.content,
        assignee_id=ticket_in.assignee_id,
        attachments=ticket_in.attachments,
    )
    
    return Success(msg="Processed Successfully")


@router.delete("/delete", summary="删除工单")
async def delete_ticket(
    ticket_id: int = Query(..., description="工单ID"),
    current_user = Depends(AuthControl.is_authed),
):
    """删除工单"""
    await ticket_controller.delete(id=ticket_id, operator_id=current_user.id)
    
    return Success(msg="Deleted Successfully")


@router.post("/upload", summary="上传附件")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(AuthControl.is_authed),
):
    """上传附件"""
    # 创建上传目录
    upload_dir = os.path.join(settings.STATIC_DIR, "uploads", "tickets")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 文件名处理
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1]
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 创建附件记录
    attachment = await ticket_controller.upload_attachment(
        file_name=original_filename,
        file_path=filename,
        file_size=file_size,
        file_type=file_extension.lstrip("."),
        uploader_id=current_user.id,
    )
    
    data = await attachment.to_dict()
    return Success(msg="Uploaded Successfully", data=data)


@router.get("/files/{filename}", summary="获取附件")
async def get_file(filename: str):
    """获取附件文件"""
    file_path = os.path.join(settings.STATIC_DIR, "uploads", "tickets", filename)
    if not os.path.exists(file_path):
        return Success(code=404, msg="File not found")
    
    return FileResponse(file_path)


@router.get("/statistics", summary="获取工单统计数据")
async def get_ticket_statistics(current_user = Depends(AuthControl.is_authed)):
    """获取工单统计数据"""
    data = await ticket_controller.get_statistics()
    
    return Success(data=data) 
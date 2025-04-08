from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from tortoise.expressions import Q
from app.controllers.toolbox import (
    toolbox_category_controller, toolbox_tool_controller,
    toolbox_template_controller
)
from app.schemas.toolbox import (
    ToolboxCategoryCreate, ToolboxCategoryUpdate, ToolboxCategoryInDB,
    ToolboxToolCreate, ToolboxToolUpdate, ToolboxToolInDB,
    ToolboxExecutionCreate, ToolboxExecutionInDB,
    ToolboxTemplateCreate, ToolboxTemplateUpdate, ToolboxTemplateInDB
)
from app.schemas import Success, SuccessExtra
from app.core.dependency import DependAuth

router = APIRouter()

# 工具箱分类相关路由
@router.get("/categories", summary="获取工具箱分类列表")
async def get_categories(
    name: str = Query(None, description="分类名称")
):
    """获取工具箱分类列表"""
    data = await toolbox_category_controller.get_category_tree(name=name)
    return Success(data=data)

@router.post("/categories", summary="创建工具箱分类")
async def create_category(
    obj_in: ToolboxCategoryCreate,
):
    """创建工具箱分类"""
    await toolbox_category_controller.create(obj_in=obj_in)
    return Success(msg="Created Successfully")

@router.put("/categories/{category_id}", summary="更新工具箱分类")
async def update_category(
    category_id: int,
    obj_in: ToolboxCategoryUpdate,
):
    """更新工具箱分类"""
    await toolbox_category_controller.update(id=category_id, obj_in=obj_in)
    return Success(msg="Update Successfully")

@router.delete("/categories/{category_id}", summary="删除工具箱分类")
async def delete_category(
    category_id: int,
):
    """删除工具箱分类"""
    await toolbox_category_controller.remove(id=category_id)
    return Success(msg="Deleted Success")

# 工具箱工具相关路由
@router.get("/tools", summary="获取工具箱工具列表")
async def get_tools(
    category_id: int = Query(None, description="分类ID"),
    name: str = Query(None, description="工具名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量")
):
    """获取工具箱工具列表"""
    total, tools = await toolbox_tool_controller.get_tool_list(
        category_id=category_id,
        name=name,
        page=page,
        page_size=page_size
    )
    data = [await obj.to_dict() for obj in tools]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/tools", summary="创建工具箱工具")
async def create_tool(
    obj_in: ToolboxToolCreate,
):
    """创建工具箱工具"""
    await toolbox_tool_controller.create(obj_in=obj_in)
    return Success(msg="Created Successfully")

@router.put("/tools/{tool_id}", summary="更新工具箱工具")
async def update_tool(
    tool_id: int,
    obj_in: ToolboxToolUpdate,
):
    """更新工具箱工具"""
    await toolbox_tool_controller.update(id=tool_id, obj_in=obj_in)
    return Success(msg="Update Successfully")

@router.delete("/tools/{tool_id}", summary="删除工具箱工具")
async def delete_tool(
    tool_id: int,
):
    """删除工具箱工具"""
    await toolbox_tool_controller.remove(id=tool_id)
    return Success(msg="Deleted Success")

@router.post("/tools/{tool_id}/execute", summary="执行工具箱工具")
async def execute_tool(
    tool_id: int,
    parameters: Dict[str, Any],
):
    """执行工具箱工具"""
    data = await toolbox_tool_controller.execute_tool(
        tool_id=tool_id,
        user_id=auth["id"],
        parameters=parameters
    )
    return Success(data=data)

# 工具箱模板相关路由
@router.get("/templates", summary="获取工具箱模板列表")
async def get_templates(
    type: int = Query(None, description="模板类型"),
    name: str = Query(None, description="模板名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量")
):
    """获取工具箱模板列表"""
    total, templates = await toolbox_template_controller.get_template_list(
        type=type,
        name=name,
        page=page,
        page_size=page_size
    )
    data = [await obj.to_dict() for obj in templates]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

@router.post("/templates", summary="创建工具箱模板")
async def create_template(
    obj_in: ToolboxTemplateCreate,
):
    """创建工具箱模板"""
    await toolbox_template_controller.create(obj_in=obj_in)
    return Success(msg="Created Successfully")

@router.put("/templates/{template_id}", summary="更新工具箱模板")
async def update_template(
    template_id: int,
    obj_in: ToolboxTemplateUpdate,
):
    """更新工具箱模板"""
    await toolbox_template_controller.update(id=template_id, obj_in=obj_in)
    return Success(msg="Update Successfully")

@router.delete("/templates/{template_id}", summary="删除工具箱模板")
async def delete_template(
    template_id: int,
):
    """删除工具箱模板"""
    await toolbox_template_controller.remove(id=template_id)
    return Success(msg="Deleted Success")

@router.post("/templates/{template_id}/render", summary="渲染工具箱模板")
async def render_template(
    template_id: int,
    variables: Dict[str, Any],
):
    """渲染工具箱模板"""
    data = await toolbox_template_controller.render_template(
        template_id=template_id,
        variables=variables
    )
    return Success(data=data) 
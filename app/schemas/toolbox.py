from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ToolboxCategoryBase(BaseModel):
    """工具箱分类基础模式"""
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, description="图标")
    order: int = Field(0, description="排序")


class ToolboxCategoryCreate(ToolboxCategoryBase):
    """创建工具箱分类"""
    pass


class ToolboxCategoryUpdate(ToolboxCategoryBase):
    """更新工具箱分类"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None


class ToolboxCategoryInDB(ToolboxCategoryBase):
    """数据库中的工具箱分类"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class ToolboxToolBase(BaseModel):
    """工具箱工具基础模式"""
    name: str = Field(..., description="工具名称")
    category_id: int = Field(..., description="所属分类ID")
    description: Optional[str] = Field(None, description="工具描述")
    icon: Optional[str] = Field(None, description="图标")
    api_path: str = Field(..., description="API路径")
    method: str = Field(..., description="请求方法")
    parameters: Dict[str, Any] = Field(..., description="参数配置")
    is_active: bool = Field(True, description="是否启用")
    order: int = Field(0, description="排序")


class ToolboxToolCreate(ToolboxToolBase):
    """创建工具箱工具"""
    pass


class ToolboxToolUpdate(ToolboxToolBase):
    """更新工具箱工具"""
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    api_path: Optional[str] = None
    method: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None


class ToolboxToolInDB(ToolboxToolBase):
    """数据库中的工具箱工具"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class ToolboxExecutionBase(BaseModel):
    """工具执行记录基础模式"""
    tool_id: int = Field(..., description="工具ID")
    parameters: Dict[str, Any] = Field(..., description="执行参数")
    result: Dict[str, Any] = Field(..., description="执行结果")
    status: int = Field(1, description="执行状态：1-成功，2-失败")
    error_message: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间(秒)")


class ToolboxExecutionCreate(ToolboxExecutionBase):
    """创建工具执行记录"""
    pass


class ToolboxExecutionInDB(ToolboxExecutionBase):
    """数据库中的工具执行记录"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True


class ToolboxTemplateBase(BaseModel):
    """工具箱模板基础模式"""
    name: str = Field(..., description="模板名称")
    type: int = Field(..., description="模板类型：1-通知模板，2-报告模板")
    content: str = Field(..., description="模板内容")
    variables: List[str] = Field(..., description="变量列表")
    is_active: bool = Field(True, description="是否启用")
    order: int = Field(0, description="排序")


class ToolboxTemplateCreate(ToolboxTemplateBase):
    """创建工具箱模板"""
    pass


class ToolboxTemplateUpdate(ToolboxTemplateBase):
    """更新工具箱模板"""
    name: Optional[str] = None
    type: Optional[int] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None


class ToolboxTemplateInDB(ToolboxTemplateBase):
    """数据库中的工具箱模板"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True 
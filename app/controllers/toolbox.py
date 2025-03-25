from typing import List, Optional, Dict, Any
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.toolbox import ToolboxCategory, ToolboxTool, ToolboxExecution, ToolboxTemplate
from app.schemas.toolbox import (
    ToolboxCategoryCreate, ToolboxCategoryUpdate,
    ToolboxToolCreate, ToolboxToolUpdate,
    ToolboxExecutionCreate,
    ToolboxTemplateCreate, ToolboxTemplateUpdate
)


class ToolboxCategoryController(CRUDBase[ToolboxCategory, ToolboxCategoryCreate, ToolboxCategoryUpdate]):
    def __init__(self):
        super().__init__(model=ToolboxCategory)

    async def get_category_tree(self, name: Optional[str] = None) -> List[Dict]:
        """获取分类树"""
        query = self.model.all()
        if name:
            query = query.filter(name__icontains=name)
        categories = await query.order_by('order').all()
        return [await category.to_dict() for category in categories]


class ToolboxToolController(CRUDBase[ToolboxTool, ToolboxToolCreate, ToolboxToolUpdate]):
    def __init__(self):
        super().__init__(model=ToolboxTool)

    async def get_tool_list(
        self,
        category_id: Optional[int] = None,
        name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[int, List[ToolboxTool]]:
        """获取工具列表"""
        query = self.model.all()
        if category_id:
            query = query.filter(category_id=category_id)
        if name:
            query = query.filter(name__icontains=name)
        
        total = await query.count()
        items = await query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    async def execute_tool(self, tool_id: int, user_id: int, parameters: Dict[str, Any]) -> Dict:
        """执行工具"""
        tool = await self.model.get_or_none(id=tool_id)
        if not tool:
            raise ValueError("工具不存在")

        # 记录执行记录
        execution = await ToolboxExecution.create(
            tool=tool,
            user_id=user_id,
            parameters=parameters
        )

        try:
            # 这里可以根据工具类型调用不同的执行逻辑
            result = {"message": "工具执行成功"}
            await execution.update(
                status="success",
                result=result
            )
            return result
        except Exception as e:
            await execution.update(
                status="failed",
                error=str(e)
            )
            raise


class ToolboxTemplateController(CRUDBase[ToolboxTemplate, ToolboxTemplateCreate, ToolboxTemplateUpdate]):
    def __init__(self):
        super().__init__(model=ToolboxTemplate)

    async def get_template_list(
        self,
        type: Optional[int] = None,
        name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[int, List[ToolboxTemplate]]:
        """获取模板列表"""
        query = self.model.all()
        if type is not None:
            query = query.filter(type=type)
        if name:
            query = query.filter(name__icontains=name)
        
        total = await query.count()
        items = await query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items

    async def render_template(self, template_id: int, variables: Dict[str, Any]) -> str:
        """渲染模板"""
        template = await self.model.get_or_none(id=template_id)
        if not template:
            raise ValueError("模板不存在")
        
        try:
            # 这里可以使用Jinja2等模板引擎进行渲染
            return template.content.format(**variables)
        except Exception as e:
            raise ValueError(f"模板渲染失败: {str(e)}")


toolbox_category_controller = ToolboxCategoryController()
toolbox_tool_controller = ToolboxToolController()
toolbox_template_controller = ToolboxTemplateController() 
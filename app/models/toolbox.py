from tortoise import fields
from tortoise.models import Model
from app.models.base import BaseModel


class ToolboxCategory(BaseModel):
    """工具箱分类"""
    name = fields.CharField(max_length=50, description="分类名称")
    description = fields.TextField(description="分类描述")
    icon = fields.CharField(max_length=50, null=True, description="图标")
    order = fields.IntField(default=0, description="排序")

    class Meta:
        table = "toolbox_categories"
        table_description = "工具箱分类表"


class ToolboxTool(BaseModel):
    """工具箱工具"""
    name = fields.CharField(max_length=50, description="工具名称")
    category = fields.ForeignKeyField('models.ToolboxCategory', related_name='tools', description="所属分类")
    description = fields.TextField(description="工具描述")
    icon = fields.CharField(max_length=50, null=True, description="图标")
    api_path = fields.CharField(max_length=100, description="API路径")
    method = fields.CharField(max_length=10, description="请求方法")
    parameters = fields.JSONField(description="参数配置")
    is_active = fields.BooleanField(default=True, description="是否启用")
    order = fields.IntField(default=0, description="排序")

    class Meta:
        table = "toolbox_tools"
        table_description = "工具箱工具表"


class ToolboxExecution(BaseModel):
    """工具执行记录"""
    tool = fields.ForeignKeyField('models.ToolboxTool', related_name='executions', description="工具")
    user = fields.ForeignKeyField('models.User', related_name='toolbox_executions', description="执行用户")
    parameters = fields.JSONField(description="执行参数")
    result = fields.JSONField(description="执行结果")
    status = fields.IntField(default=1, description="执行状态：1-成功，2-失败")
    error_message = fields.TextField(null=True, description="错误信息")
    execution_time = fields.FloatField(description="执行时间(秒)")

    class Meta:
        table = "toolbox_executions"
        table_description = "工具执行记录表"


class ToolboxTemplate(BaseModel):
    """工具箱模板"""
    name = fields.CharField(max_length=50, description="模板名称")
    type = fields.IntField(description="模板类型：1-通知模板，2-报告模板")
    content = fields.TextField(description="模板内容")
    variables = fields.JSONField(description="变量列表")
    is_active = fields.BooleanField(default=True, description="是否启用")
    order = fields.IntField(default=0, description="排序")

    class Meta:
        table = "toolbox_templates"
        table_description = "工具箱模板表" 
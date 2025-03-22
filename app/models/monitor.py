from tortoise import fields
from .base import BaseModel, TimestampMixin

class HostGroup(BaseModel, TimestampMixin):
    """主机分组"""
    name = fields.CharField(max_length=64, description="分组名称", index=True)
    is_default = fields.BooleanField(default=False, description="是否为默认分组")
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "monitor_host_group"

class MonitorHost(BaseModel, TimestampMixin):
    """监控主机"""
    name = fields.CharField(max_length=64, description="主机名称", index=True)
    group = fields.ForeignKeyField('models.HostGroup', related_name='hosts')
    ip = fields.CharField(max_length=64, description="IP地址", index=True)
    port = fields.IntField(default=22, description="SSH端口")
    username = fields.CharField(max_length=32, description="用户名")
    auth_type = fields.CharField(max_length=16, description="认证方式", default="password") # password/key
    password = fields.CharField(max_length=256, null=True, description="密码")
    private_key = fields.TextField(null=True, description="私钥内容") 
    status = fields.CharField(max_length=16, default="unknown", description="状态") # up/down/unknown
    remark = fields.CharField(max_length=255, null=True, description="备注")

    class Meta:
        table = "monitor_host" 

# 添加初始化默认分组的函数
async def init_default_host_group():
    default_group = await HostGroup.filter(is_default=True).first()
    if not default_group:
        await HostGroup.create(
            name="默认分组",
            is_default=True,
            remark="系统默认分组"
        ) 
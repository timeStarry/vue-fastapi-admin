from tortoise import fields

from .base import BaseModel, TimestampMixin


class AssetCategory(BaseModel, TimestampMixin):
    """资产分类"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, description="分类名称")
    desc = fields.CharField(max_length=200, null=True, description="分类描述")
    type = fields.IntField(default=1, description="类型：1-主机，2-服务")
    order = fields.IntField(default=0, description="排序")
    is_deleted = fields.BooleanField(default=False, description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "monitor_asset_category"
        table_description = "资产分类表"


class Asset(BaseModel, TimestampMixin):
    """资产信息"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="资产名称")
    category_id = fields.IntField(description="资产分类ID")
    type = fields.IntField(default=1, description="类型：1-主机，2-服务")
    status = fields.IntField(default=1, description="状态：1-正常，2-异常，3-离线")
    desc = fields.CharField(max_length=200, null=True, description="描述")
    is_deleted = fields.BooleanField(default=False, description="是否删除")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "monitor_asset"
        table_description = "资产信息表"


class HostAsset(BaseModel, TimestampMixin):
    """主机资产"""
    id = fields.IntField(pk=True)
    asset_id = fields.IntField(description="关联的资产ID")
    ip_address = fields.CharField(max_length=50, description="IP地址")
    mac_address = fields.CharField(max_length=50, null=True, description="MAC地址")
    cpu_usage = fields.FloatField(null=True, description="CPU使用率")
    memory_usage = fields.FloatField(null=True, description="内存使用率")
    disk_usage = fields.FloatField(null=True, description="磁盘使用率")
    last_check_time = fields.DatetimeField(null=True, description="最后检查时间")
    ping_status = fields.BooleanField(default=True, description="Ping状态")
    ping_response_time = fields.IntField(null=True, description="Ping响应时间(ms)")

    class Meta:
        table = "monitor_host_asset"
        table_description = "主机资产表"


class ServiceAsset(BaseModel, TimestampMixin):
    """服务资产"""
    id = fields.IntField(pk=True)
    asset_id = fields.IntField(description="关联的资产ID")
    url = fields.CharField(max_length=255, description="服务URL")
    method = fields.CharField(max_length=10, default="GET", description="请求方法")
    expected_status_code = fields.IntField(default=200, description="期望的状态码")
    check_interval = fields.IntField(default=300, description="检查间隔(秒)")
    timeout = fields.IntField(default=5, description="超时时间(秒)")
    last_check_time = fields.DatetimeField(null=True, description="最后检查时间")
    last_status_code = fields.IntField(null=True, description="最后状态码")
    last_response_time = fields.IntField(null=True, description="最后响应时间(ms)")
    is_ssl = fields.BooleanField(default=False, description="是否SSL")
    verify_ssl = fields.BooleanField(default=True, description="是否验证SSL")
    headers = fields.JSONField(null=True, description="请求头")
    body = fields.JSONField(null=True, description="请求体")

    class Meta:
        table = "monitor_service_asset"
        table_description = "服务资产表"


class AssetAlert(BaseModel, TimestampMixin):
    """资产告警"""
    id = fields.IntField(pk=True)
    asset_id = fields.IntField(description="资产ID")
    alert_type = fields.IntField(description="告警类型：1-CPU告警，2-内存告警，3-磁盘告警，4-Ping告警，5-服务状态码告警，6-服务响应时间告警")
    alert_level = fields.IntField(description="告警级别：1-低，2-中，3-高")
    alert_content = fields.CharField(max_length=500, description="告警内容")
    is_resolved = fields.BooleanField(default=False, description="是否已解决")
    resolved_time = fields.DatetimeField(null=True, description="解决时间")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "monitor_asset_alert"
        table_description = "资产告警表"
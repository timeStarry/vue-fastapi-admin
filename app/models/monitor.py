from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models.base import BaseModel, TimestampMixin
from app.models.admin import User


class MonitorHost(BaseModel, TimestampMixin):
    """主机监控模型"""
    host_name = fields.CharField(max_length=100, description="主机名", index=True)
    ip = fields.CharField(max_length=50, description="IP地址", index=True)
    status = fields.CharField(max_length=20, description="状态", default="unknown", index=True)  # online, offline, unknown
    host_type = fields.CharField(max_length=50, description="主机类型", index=True)  # server, router, switch, firewall, other
    enable_mrtg = fields.BooleanField(description="启用MRTG", default=False)
    mrtg_status = fields.CharField(max_length=20, description="MRTG状态", null=True, index=True)  # normal, abnormal, null
    last_online_time = fields.DatetimeField(description="最后在线时间", null=True, index=True)
    ping_interval = fields.IntField(description="Ping间隔(秒)", default=60)
    remark = fields.TextField(description="备注", null=True)

    class Meta:
        table = "monitor_host"
        table_description = "主机监控表"

    def __str__(self):
        return f"{self.host_name} ({self.ip})"

    async def to_dict(self, include_records=False):
        result = {
            "id": self.id,
            "host_name": self.host_name,
            "ip": self.ip,
            "status": self.status,
            "host_type": self.host_type,
            "enable_mrtg": self.enable_mrtg,
            "mrtg_status": self.mrtg_status,
            "last_online_time": self.last_online_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_online_time else None,
            "ping_interval": self.ping_interval,
            "remark": self.remark,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        if include_records:
            # 获取监控记录
            ping_records = await MonitorHostRecord.filter(host_id=self.id).order_by("-created_at").limit(10)
            result["ping_records"] = [await record.to_dict() for record in ping_records]
            
        return result


class MonitorHostRecord(BaseModel, TimestampMixin):
    """主机监控记录"""
    host = fields.ForeignKeyField("models.MonitorHost", related_name="ping_records", description="主机")
    status = fields.CharField(max_length=20, description="状态", index=True)  # online, offline
    response_time = fields.IntField(description="响应时间(ms)", null=True)
    packet_loss = fields.FloatField(description="丢包率", null=True)

    class Meta:
        table = "monitor_host_record"
        table_description = "主机监控记录表"

    def __str__(self):
        return f"{self.host.host_name} - {self.status}"
    
    async def to_dict(self):
        host = await self.host
        return {
            "id": self.id,
            "host_id": self.host_id,
            "host_name": host.host_name,
            "status": self.status,
            "response_time": self.response_time,
            "packet_loss": self.packet_loss,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MonitorMRTGData(BaseModel, TimestampMixin):
    """MRTG监控数据"""
    host = fields.ForeignKeyField("models.MonitorHost", related_name="mrtg_data", description="主机")
    in_traffic = fields.FloatField(description="入流量(Mbps)")
    out_traffic = fields.FloatField(description="出流量(Mbps)")
    cpu_usage = fields.FloatField(description="CPU使用率(%)")
    memory_usage = fields.FloatField(description="内存使用率(%)")
    disk_usage = fields.FloatField(description="磁盘使用率(%)")

    class Meta:
        table = "monitor_mrtg_data"
        table_description = "MRTG监控数据表"

    def __str__(self):
        return f"{self.host.host_name} - {self.created_at}"

    async def to_dict(self):
        host = await self.host
        return {
            "id": self.id,
            "host_id": self.host_id,
            "host_name": host.host_name,
            "in_traffic": self.in_traffic,
            "out_traffic": self.out_traffic,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MonitorService(BaseModel, TimestampMixin):
    """服务监控模型"""
    service_name = fields.CharField(max_length=100, description="服务名称", index=True)
    url = fields.CharField(max_length=255, description="服务URL", index=True)
    service_type = fields.CharField(max_length=50, description="服务类型", index=True)  # web, api, database, cache, other
    status = fields.CharField(max_length=20, description="状态", default="unknown", index=True)  # normal, warning, error, unknown
    check_method = fields.CharField(max_length=50, description="检测方法", index=True)  # http_get, http_post, tcp, ping
    expected_status = fields.CharField(max_length=50, description="预期状态码", default="200")
    last_response_time = fields.IntField(description="最后响应时间(ms)", null=True)
    last_check_time = fields.DatetimeField(description="最后检测时间", null=True, index=True)
    check_interval = fields.IntField(description="检测间隔(秒)", default=60)
    timeout = fields.IntField(description="超时时间(秒)", default=5)
    host = fields.ForeignKeyField("models.MonitorHost", related_name="services", description="关联主机", null=True)
    remark = fields.TextField(description="备注", null=True)

    class Meta:
        table = "monitor_service"
        table_description = "服务监控表"

    def __str__(self):
        return self.service_name

    async def to_dict(self, include_records=False):
        host_obj = await self.host if self.host_id else None
        
        result = {
            "id": self.id,
            "service_name": self.service_name,
            "url": self.url,
            "service_type": self.service_type,
            "status": self.status,
            "check_method": self.check_method,
            "expected_status": self.expected_status,
            "last_response_time": self.last_response_time,
            "last_check_time": self.last_check_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_check_time else None,
            "check_interval": self.check_interval,
            "timeout": self.timeout,
            "host_id": self.host_id,
            "host_name": host_obj.host_name if host_obj else None,
            "host_ip": host_obj.ip if host_obj else None,
            "remark": self.remark,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        if include_records:
            # 获取服务检测记录
            check_records = await MonitorServiceRecord.filter(service_id=self.id).order_by("-created_at").limit(10)
            result["check_records"] = [await record.to_dict() for record in check_records]
            
        return result


class MonitorServiceRecord(BaseModel, TimestampMixin):
    """服务监控记录"""
    service = fields.ForeignKeyField("models.MonitorService", related_name="check_records", description="服务")
    status = fields.CharField(max_length=20, description="状态", index=True)  # normal, warning, error, unknown
    response_time = fields.IntField(description="响应时间(ms)", null=True)
    status_code = fields.IntField(description="状态码", null=True)
    content = fields.TextField(description="响应内容", null=True)

    class Meta:
        table = "monitor_service_record"
        table_description = "服务监控记录表"

    def __str__(self):
        return f"{self.service.service_name} - {self.status}"

    async def to_dict(self):
        service = await self.service
        return {
            "id": self.id,
            "service_id": self.service_id,
            "service_name": service.service_name,
            "status": self.status,
            "response_time": self.response_time,
            "status_code": self.status_code,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MonitorAlert(BaseModel, TimestampMixin):
    """监控告警"""
    level = fields.CharField(max_length=20, description="级别", index=True)  # error, warning, info
    target_type = fields.CharField(max_length=20, description="目标类型", index=True)  # host, service
    target_id = fields.IntField(description="目标ID", index=True)
    target_name = fields.CharField(max_length=100, description="目标名称", index=True)
    target_ip = fields.CharField(max_length=50, description="目标IP", null=True, index=True)
    alert_type = fields.CharField(max_length=50, description="告警类型", index=True)
    content = fields.TextField(description="告警内容")
    resolved = fields.BooleanField(description="是否已解决", default=False, index=True)
    resolved_at = fields.DatetimeField(description="解决时间", null=True, index=True)
    details = fields.JSONField(description="详细信息", null=True)

    class Meta:
        table = "monitor_alert"
        table_description = "监控告警表"

    def __str__(self):
        return f"{self.target_name} - {self.alert_type}"

    async def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "target_ip": self.target_ip,
            "alert_type": self.alert_type,
            "content": self.content,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if self.resolved_at else None,
            "details": self.details,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        } 
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator, Field

# 主机监控相关schema
class HostCreate(BaseModel):
    host_name: str = Field(..., description="主机名")
    ip: str = Field(..., description="IP地址")
    host_type: str = Field(..., description="主机类型")
    ping_interval: int = Field(60, description="Ping间隔(秒)")
    enable_mrtg: bool = Field(False, description="是否启用MRTG")
    remark: Optional[str] = Field(None, description="备注")

    @validator('ip')
    def validate_ip(cls, v):
        # 简单的IP地址验证
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('IP地址格式不正确')
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError('IP地址格式不正确')
            except ValueError:
                raise ValueError('IP地址格式不正确')
        return v

class HostUpdate(BaseModel):
    host_name: Optional[str] = Field(None, description="主机名")
    ip: Optional[str] = Field(None, description="IP地址")
    host_type: Optional[str] = Field(None, description="主机类型")
    ping_interval: Optional[int] = Field(None, description="Ping间隔(秒)")
    enable_mrtg: Optional[bool] = Field(None, description="是否启用MRTG")
    remark: Optional[str] = Field(None, description="备注")

    @validator('ip')
    def validate_ip(cls, v):
        if v is None:
            return v
        # 简单的IP地址验证
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('IP地址格式不正确')
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError('IP地址格式不正确')
            except ValueError:
                raise ValueError('IP地址格式不正确')
        return v

class PingTestResult(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    data: Optional[dict] = Field(None, description="数据")


# 服务监控相关schema
class ServiceCreate(BaseModel):
    service_name: str = Field(..., description="服务名称")
    url: str = Field(..., description="服务URL")
    service_type: str = Field(..., description="服务类型")
    check_method: str = Field(..., description="检测方法")
    expected_status: str = Field("200", description="预期状态码")
    check_interval: int = Field(60, description="检测间隔(秒)")
    timeout: int = Field(5, description="超时时间(秒)")
    host_id: Optional[int] = Field(None, description="关联主机ID")
    remark: Optional[str] = Field(None, description="备注")

class ServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(None, description="服务名称")
    url: Optional[str] = Field(None, description="服务URL")
    service_type: Optional[str] = Field(None, description="服务类型")
    check_method: Optional[str] = Field(None, description="检测方法")
    expected_status: Optional[str] = Field(None, description="预期状态码")
    check_interval: Optional[int] = Field(None, description="检测间隔(秒)")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")
    host_id: Optional[int] = Field(None, description="关联主机ID")
    remark: Optional[str] = Field(None, description="备注")

class ServiceTestResult(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    data: Optional[dict] = Field(None, description="数据")


# 监控面板相关schema
class DashboardData(BaseModel):
    host_count: int = Field(..., description="主机总数")
    service_count: int = Field(..., description="服务总数")
    online_host_count: int = Field(..., description="在线主机数")
    normal_service_count: int = Field(..., description="正常服务数")
    alert_count: int = Field(..., description="告警总数")
    unresolved_alert_count: int = Field(..., description="未解决告警数")

    host_status_distribution: dict = Field(..., description="主机状态分布")
    service_status_distribution: dict = Field(..., description="服务状态分布")
    alert_level_distribution: dict = Field(..., description="告警级别分布")
    recent_alerts: List[dict] = Field(..., description="最近告警")


# 告警相关schema
class AlertUpdate(BaseModel):
    resolved: bool = Field(..., description="是否已解决") 
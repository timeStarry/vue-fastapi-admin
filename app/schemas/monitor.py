from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class AssetCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    desc: Optional[str] = Field(None, description="分类描述")
    type: int = Field(1, description="类型：1-主机，2-服务")
    order: int = Field(0, description="排序")


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryUpdate(AssetCategoryBase):
    pass


class AssetCategoryInDB(AssetCategoryBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    name: str = Field(..., description="资产名称")
    category_id: int = Field(..., description="资产分类ID")
    type: int = Field(1, description="类型：1-主机，2-服务")
    status: int = Field(1, description="状态：1-正常，2-异常，3-离线")
    desc: Optional[str] = Field(None, description="描述")


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    id: int


class AssetInDB(AssetBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HostAssetBase(BaseModel):
    ip_address: str = Field(..., description="IP地址")
    mac_address: Optional[str] = Field(None, description="MAC地址")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率")
    memory_usage: Optional[float] = Field(None, description="内存使用率")
    disk_usage: Optional[float] = Field(None, description="磁盘使用率")
    ping_status: bool = Field(True, description="Ping状态")
    ping_response_time: Optional[int] = Field(None, description="Ping响应时间(ms)")


class HostAssetCreate(HostAssetBase):
    asset_id: int = Field(..., description="关联的资产ID")


class HostAssetUpdate(HostAssetBase):
    id: int


class HostAssetInDB(HostAssetBase):
    id: int
    asset_id: int
    last_check_time: Optional[datetime]

    class Config:
        from_attributes = True


class ServiceAssetBase(BaseModel):
    url: str = Field(..., description="服务URL")
    method: str = Field("GET", description="请求方法")
    expected_status_code: int = Field(200, description="期望的状态码")
    check_interval: int = Field(300, description="检查间隔(秒)")
    timeout: int = Field(5, description="超时时间(秒)")
    is_ssl: bool = Field(False, description="是否SSL")
    verify_ssl: bool = Field(True, description="是否验证SSL")
    headers: Optional[Dict[str, Any]] = Field(None, description="请求头")
    body: Optional[Dict[str, Any]] = Field(None, description="请求体")


class ServiceAssetCreate(ServiceAssetBase):
    asset_id: int = Field(..., description="关联的资产ID")


class ServiceAssetUpdate(ServiceAssetBase):
    id: int


class ServiceAssetInDB(ServiceAssetBase):
    id: int
    asset_id: int
    last_check_time: Optional[datetime]
    last_status_code: Optional[int]
    last_response_time: Optional[int]

    class Config:
        from_attributes = True


class AssetAlertBase(BaseModel):
    asset_id: int = Field(..., description="资产ID")
    alert_type: int = Field(..., description="告警类型：1-CPU告警，2-内存告警，3-磁盘告警，4-Ping告警，5-服务状态码告警，6-服务响应时间告警")
    alert_level: int = Field(..., description="告警级别：1-低，2-中，3-高")
    alert_content: str = Field(..., description="告警内容")
    is_resolved: bool = Field(False, description="是否已解决")


class AssetAlertCreate(AssetAlertBase):
    pass


class AssetAlertUpdate(AssetAlertBase):
    id: int
    resolved_time: Optional[datetime]


class AssetAlertInDB(AssetAlertBase):
    id: int
    resolved_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

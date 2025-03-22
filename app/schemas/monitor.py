from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HostGroupBase(BaseModel):
    name: str = Field(..., description="分组名称")
    remark: Optional[str] = Field(None, description="备注")
    is_default: Optional[bool] = Field(False, description="是否为默认分组")

class HostGroupCreate(HostGroupBase):
    pass

class HostGroupUpdate(HostGroupBase):
    pass

class HostGroupOut(HostGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime

class MonitorHostBase(BaseModel):
    name: str = Field(..., description="主机名称")
    group_id: int = Field(..., description="分组ID")
    ip: str = Field(..., description="IP地址")
    port: int = Field(22, description="SSH端口")
    username: str = Field(..., description="用户名")
    auth_type: str = Field("password", description="认证方式")
    password: Optional[str] = Field(None, description="密码")
    private_key: Optional[str] = Field(None, description="私钥内容")
    remark: Optional[str] = Field(None, description="备注")

class MonitorHostCreate(MonitorHostBase):
    pass

class MonitorHostUpdate(MonitorHostBase):
    pass

class MonitorHostOut(MonitorHostBase):
    id: int
    status: str
    group_name: str
    created_at: datetime
    updated_at: datetime

class MonitorHostList(BaseModel):
    items: List[MonitorHostOut]
    total: int
    page: int
    page_size: int 
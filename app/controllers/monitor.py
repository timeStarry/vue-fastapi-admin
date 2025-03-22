from typing import List, Optional
from tortoise.expressions import Q
from tortoise.transactions import atomic

from app.core.crud import CRUDBase
from app.models.monitor import HostGroup, MonitorHost
from app.schemas.monitor import (
    HostGroupCreate, HostGroupUpdate, HostGroupOut,
    MonitorHostCreate, MonitorHostUpdate, MonitorHostOut, MonitorHostList
)
from app.utils.ssh import test_ssh_connection
from app.utils.ping import ping_host

class HostGroupController(CRUDBase[HostGroup, HostGroupCreate, HostGroupUpdate]):
    def __init__(self):
        super().__init__(model=HostGroup)

    async def get_list(self, page: int = 1, page_size: int = 10, **kwargs) -> tuple[int, List[dict]]:
        """获取分组列表"""
        q = Q()
        if name := kwargs.get('name'):
            q &= Q(name__contains=name)
        
        total, groups = await self.list(page=page, page_size=page_size, search=q)
        data = [await group.to_dict() for group in groups]
        return total, data

    @atomic()
    async def set_default(self, group_id: int) -> None:
        """设置默认分组"""
        await self.model.filter(is_default=True).update(is_default=False)
        await self.model.filter(id=group_id).update(is_default=True)

class MonitorHostController(CRUDBase[MonitorHost, MonitorHostCreate, MonitorHostUpdate]):
    def __init__(self):
        super().__init__(model=MonitorHost)

    async def get_list(self, page: int = 1, page_size: int = 10, **kwargs) -> dict:
        """获取主机列表"""
        query = Q()
        if name := kwargs.get('name'):
            query &= Q(name__icontains=name)
        if ip := kwargs.get('ip'):
            query &= Q(ip__icontains=ip)
        if group_id := kwargs.get('group_id'):
            query &= Q(group_id=group_id)
        if id := kwargs.get('id'):
            query &= Q(id=id)
        
        total, hosts = await self.list(page=page, page_size=page_size, search=query)
        
        items = []
        for host in hosts:
            host_dict = await host.to_dict()
            host_dict['group_name'] = (await host.group).name
            items.append(host_dict)
            
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def test_connection(self, host_data: dict) -> dict:
        """测试主机连接"""
        # 先进行Ping测试
        ping_success, ping_message = await ping_host(host_data['ip'])
        
        if not ping_success:
            if host_id := host_data.get('id'):
                await self.model.filter(id=host_id).update(status='down')
            return {"code": 400, "msg": ping_message}
        
        # Ping成功，先将状态设置为up
        status = 'up'
        if host_id := host_data.get('id'):
            await self.model.filter(id=host_id).update(status=status)
        
        # 测试SSH连接
        ssh_success, ssh_message = await test_ssh_connection(
            hostname=host_data['ip'],
            port=host_data['port'],
            username=host_data['username'],
            password=host_data.get('password'),
            private_key=host_data.get('private_key')
        )
        
        # 如果SSH连接成功，更新状态为useful
        if ssh_success:
            status = 'useful'
            if host_id := host_data.get('id'):
                await self.model.filter(id=host_id).update(status=status)
        
        return {
            "code": 200, 
            "msg": ssh_message if ssh_success else "主机可达，但SSH连接失败"
        }

    async def create(self, obj_in: MonitorHostCreate) -> MonitorHost:
        """创建主机时设置初始状态为unknown"""
        obj_dict = obj_in.model_dump()
        obj_dict['status'] = 'unknown'  # 设置初始状态
        return await super().create(obj_dict)

host_group_controller = HostGroupController()
monitor_host_controller = MonitorHostController() 
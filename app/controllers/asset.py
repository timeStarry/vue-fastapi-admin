from tortoise.expressions import Q
from tortoise.transactions import atomic
from datetime import datetime
import aiohttp
import asyncio
import platform
import subprocess
from typing import Optional, List, Dict, Any

from app.core.crud import CRUDBase
from app.models.admin import Asset, AssetCategory, AssetAlert, HostAsset, ServiceAsset
from app.schemas.assets import (
    AssetCreate, AssetUpdate, AssetCategoryCreate, AssetCategoryUpdate,
    AssetAlertCreate, AssetAlertUpdate, HostAssetCreate, HostAssetUpdate,
    ServiceAssetCreate, ServiceAssetUpdate
)


class AssetCategoryController(CRUDBase[AssetCategory, AssetCategoryCreate, AssetCategoryUpdate]):
    def __init__(self):
        super().__init__(model=AssetCategory)

    async def get_category_tree(self, name: str = None, type: int = None):
        q = Q()
        q &= Q(is_deleted=False)
        if name:
            q &= Q(name__contains=name)
        if type:
            q &= Q(type=type)
        all_categories = await self.model.filter(q).order_by("order")
        
        def build_tree(parent_id=0):
            return [
                {
                    "id": category.id,
                    "name": category.name,
                    "desc": category.desc,
                    "type": category.type,
                    "order": category.order,
                    "children": build_tree(category.id)
                }
                for category in all_categories
                if category.parent_id == parent_id
            ]
        
        return build_tree()


class AssetController(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    def __init__(self):
        super().__init__(model=Asset)

    async def get_asset_list(self, category_id: int = None, status: int = None, 
                           name: str = None, type: int = None):
        q = Q()
        q &= Q(is_deleted=False)
        if category_id:
            q &= Q(category_id=category_id)
        if status:
            q &= Q(status=status)
        if name:
            q &= Q(name__contains=name)
        if type:
            q &= Q(type=type)
        return await self.model.filter(q).order_by("-created_at")

    @atomic()
    async def create_asset(self, obj_in: AssetCreate):
        # 验证分类是否存在
        category = await AssetCategory.get(id=obj_in.category_id)
        if category.type != obj_in.type:
            raise ValueError("资产类型与分类类型不匹配")
        return await self.create(obj_in=obj_in)

    @atomic()
    async def update_asset(self, obj_in: AssetUpdate):
        # 验证分类是否存在
        if obj_in.category_id:
            category = await AssetCategory.get(id=obj_in.category_id)
            if category.type != obj_in.type:
                raise ValueError("资产类型与分类类型不匹配")
        return await self.update(obj_in=obj_in)


class HostAssetController(CRUDBase[HostAsset, HostAssetCreate, HostAssetUpdate]):
    def __init__(self):
        super().__init__(model=HostAsset)

    async def get_host_asset(self, asset_id: int):
        return await self.model.get(asset_id=asset_id)

    async def update_host_status(self, asset_id: int, cpu_usage: float = None,
                               memory_usage: float = None, disk_usage: float = None,
                               ping_status: bool = None, ping_response_time: int = None):
        host = await self.get_host_asset(asset_id)
        if not host:
            return None

        update_data = {
            "last_check_time": datetime.now()
        }
        if cpu_usage is not None:
            update_data["cpu_usage"] = cpu_usage
        if memory_usage is not None:
            update_data["memory_usage"] = memory_usage
        if disk_usage is not None:
            update_data["disk_usage"] = disk_usage
        if ping_status is not None:
            update_data["ping_status"] = ping_status
        if ping_response_time is not None:
            update_data["ping_response_time"] = ping_response_time

        await host.update_from_dict(update_data).save()
        return host

    async def check_host_status(self, host: HostAsset) -> Dict[str, Any]:
        """检查主机状态"""
        # 检查ping状态
        ping_status = False
        ping_response_time = None
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', host.ip_address]
            start_time = datetime.now()
            response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            end_time = datetime.now()
            ping_status = response.returncode == 0
            ping_response_time = int((end_time - start_time).total_seconds() * 1000)
        except Exception as e:
            print(f"Ping error: {str(e)}")

        # 更新状态
        await self.update_host_status(
            host.asset_id,
            ping_status=ping_status,
            ping_response_time=ping_response_time
        )

        # 创建告警
        if not ping_status:
            await AssetAlert.create(
                asset_id=host.asset_id,
                alert_type=4,  # Ping告警
                alert_level=2,  # 中级别
                alert_content=f"主机 {host.ip_address} Ping失败"
            )

        return {
            "ping_status": ping_status,
            "ping_response_time": ping_response_time
        }


class ServiceAssetController(CRUDBase[ServiceAsset, ServiceAssetCreate, ServiceAssetUpdate]):
    def __init__(self):
        super().__init__(model=ServiceAsset)

    async def get_service_asset(self, asset_id: int):
        return await self.model.get(asset_id=asset_id)

    async def update_service_status(self, asset_id: int, status_code: int = None,
                                  response_time: int = None):
        service = await self.get_service_asset(asset_id)
        if not service:
            return None

        update_data = {
            "last_check_time": datetime.now()
        }
        if status_code is not None:
            update_data["last_status_code"] = status_code
        if response_time is not None:
            update_data["last_response_time"] = response_time

        await service.update_from_dict(update_data).save()
        return service

    async def check_service_status(self, service: ServiceAsset) -> Dict[str, Any]:
        """检查服务状态"""
        status_code = None
        response_time = None
        is_ok = False

        try:
            async with aiohttp.ClientSession() as session:
                start_time = datetime.now()
                async with session.request(
                    method=service.method,
                    url=service.url,
                    headers=service.headers,
                    json=service.body,
                    ssl=service.verify_ssl if service.is_ssl else None,
                    timeout=service.timeout
                ) as response:
                    end_time = datetime.now()
                    status_code = response.status
                    response_time = int((end_time - start_time).total_seconds() * 1000)
                    is_ok = status_code == service.expected_status_code
        except Exception as e:
            print(f"Service check error: {str(e)}")

        # 更新状态
        await self.update_service_status(
            service.asset_id,
            status_code=status_code,
            response_time=response_time
        )

        # 创建告警
        if not is_ok:
            alert_type = 5 if status_code != service.expected_status_code else 6
            alert_content = (
                f"服务 {service.url} 状态码异常: {status_code}"
                if alert_type == 5
                else f"服务 {service.url} 响应时间过长: {response_time}ms"
            )
            await AssetAlert.create(
                asset_id=service.asset_id,
                alert_type=alert_type,
                alert_level=2,
                alert_content=alert_content
            )

        return {
            "status_code": status_code,
            "response_time": response_time,
            "is_ok": is_ok
        }


class AssetAlertController(CRUDBase[AssetAlert, AssetAlertCreate, AssetAlertUpdate]):
    def __init__(self):
        super().__init__(model=AssetAlert)

    async def get_alert_list(self, asset_id: int = None, alert_type: int = None,
                           alert_level: int = None, is_resolved: bool = None):
        q = Q()
        if asset_id:
            q &= Q(asset_id=asset_id)
        if alert_type:
            q &= Q(alert_type=alert_type)
        if alert_level:
            q &= Q(alert_level=alert_level)
        if is_resolved is not None:
            q &= Q(is_resolved=is_resolved)
        return await self.model.filter(q).order_by("-created_at")

    @atomic()
    async def create_alert(self, obj_in: AssetAlertCreate):
        # 验证资产是否存在
        await Asset.get(id=obj_in.asset_id)
        return await self.create(obj_in=obj_in)

    @atomic()
    async def resolve_alert(self, alert_id: int):
        alert = await self.get(id=alert_id)
        alert.is_resolved = True
        alert.resolved_time = datetime.now()
        await alert.save()


asset_category_controller = AssetCategoryController()
asset_controller = AssetController()
host_asset_controller = HostAssetController()
service_asset_controller = ServiceAssetController()
asset_alert_controller = AssetAlertController() 
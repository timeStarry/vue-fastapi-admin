import asyncio
import datetime
import subprocess
import re
import aiohttp
import random
import concurrent.futures
from typing import List, Dict, Optional, Any, Union

# 移除SNMP相关模块导入
# 改为使用模拟数据

from app.models.monitor import (
    MonitorHost, MonitorHostRecord, MonitorMRTGData,
    MonitorService, MonitorServiceRecord, MonitorAlert
)
from app.schemas.monitor import (
    HostCreate, HostUpdate, PingTestResult,
    ServiceCreate, ServiceUpdate, ServiceTestResult, 
    DashboardData, AlertUpdate
)

# 替换为系统日志
from app.log import logger

# SNMP常用OID定义
SNMP_OIDS = {
    # 接口信息
    "ifNumber": "1.3.6.1.2.1.2.1.0",                # 接口数量
    "ifTable": "1.3.6.1.2.1.2.2",                   # 接口表
    "ifEntry": "1.3.6.1.2.1.2.2.1",                 # 接口表条目
    "ifIndex": "1.3.6.1.2.1.2.2.1.1",               # 接口索引
    "ifDescr": "1.3.6.1.2.1.2.2.1.2",               # 接口描述
    "ifType": "1.3.6.1.2.1.2.2.1.3",                # 接口类型
    "ifMtu": "1.3.6.1.2.1.2.2.1.4",                 # 接口MTU
    "ifSpeed": "1.3.6.1.2.1.2.2.1.5",               # 接口速度
    "ifPhysAddress": "1.3.6.1.2.1.2.2.1.6",         # 接口物理地址
    "ifAdminStatus": "1.3.6.1.2.1.2.2.1.7",         # 接口管理状态
    "ifOperStatus": "1.3.6.1.2.1.2.2.1.8",          # 接口操作状态
    "ifInOctets": "1.3.6.1.2.1.2.2.1.10",           # 接口入字节数
    "ifInUcastPkts": "1.3.6.1.2.1.2.2.1.11",        # 接口入单播包数
    "ifInErrors": "1.3.6.1.2.1.2.2.1.14",           # 接口入错误数
    "ifOutOctets": "1.3.6.1.2.1.2.2.1.16",          # 接口出字节数
    "ifOutUcastPkts": "1.3.6.1.2.1.2.2.1.17",       # 接口出单播包数
    "ifOutErrors": "1.3.6.1.2.1.2.2.1.20",          # 接口出错误数
    
    # 系统信息
    "sysDescr": "1.3.6.1.2.1.1.1.0",                # 系统描述
    "sysUpTime": "1.3.6.1.2.1.1.3.0",               # 系统运行时间
    "sysName": "1.3.6.1.2.1.1.5.0",                 # 系统名称
    
    # CPU和内存
    "hrProcessorLoad": "1.3.6.1.2.1.25.3.3.1.2",    # CPU负载(HOST-RESOURCES-MIB)
    "memTotalReal": "1.3.6.1.4.1.2021.4.5.0",       # 物理内存总量(UCD-SNMP-MIB)
    "memAvailReal": "1.3.6.1.4.1.2021.4.6.0",       # 可用物理内存(UCD-SNMP-MIB)
    "memTotalFree": "1.3.6.1.4.1.2021.4.11.0",      # 总空闲内存(UCD-SNMP-MIB)
    "memShared": "1.3.6.1.4.1.2021.4.13.0",         # 共享内存(UCD-SNMP-MIB)
    "memBuffer": "1.3.6.1.4.1.2021.4.14.0",         # 缓冲内存(UCD-SNMP-MIB)
    "memCached": "1.3.6.1.4.1.2021.4.15.0",         # 缓存内存(UCD-SNMP-MIB)
    
    # 磁盘
    "dskTable": "1.3.6.1.4.1.2021.9",               # 磁盘表(UCD-SNMP-MIB)
    "dskEntry": "1.3.6.1.4.1.2021.9.1",             # 磁盘表条目
    "dskPath": "1.3.6.1.4.1.2021.9.1.2",            # 磁盘路径
    "dskTotal": "1.3.6.1.4.1.2021.9.1.6",           # 磁盘总大小
    "dskAvail": "1.3.6.1.4.1.2021.9.1.7",           # 磁盘可用大小
    "dskUsed": "1.3.6.1.4.1.2021.9.1.8",            # 磁盘已用大小
    "dskPercent": "1.3.6.1.4.1.2021.9.1.9",         # 磁盘使用率
}

class MonitorController:
    """监控控制器"""

    @staticmethod
    async def get_host_list(
        page: int = 1, 
        page_size: int = 10, 
        host_name: Optional[str] = None,
        ip: Optional[str] = None,
        status: Optional[str] = None,
        host_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取主机列表"""
        # 构建查询条件
        query = {}
        if host_name:
            query["host_name__contains"] = host_name
        if ip:
            query["ip__contains"] = ip
        if status:
            query["status"] = status
        if host_type:
            query["host_type"] = host_type
            
        # 查询总数
        total = await MonitorHost.filter(**query).count()
        
        # 分页查询
        hosts = await MonitorHost.filter(**query).offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        host_list = [await host.to_dict() for host in hosts]
        
        return {
            "items": host_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_host(host_data: HostCreate) -> Dict[str, Any]:
        """创建主机"""
        host = await MonitorHost.create(
            host_name=host_data.host_name,
            ip=host_data.ip,
            host_type=host_data.host_type,
            ping_interval=host_data.ping_interval,
            enable_mrtg=host_data.enable_mrtg,
            remark=host_data.remark
        )
        
        # 创建时进行一次Ping测试
        ping_result = await MonitorController.ping_host(host.id)
        
        return await host.to_dict()
    
    @staticmethod
    async def get_host(host_id: int) -> Dict[str, Any]:
        """获取主机详情"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host:
            return None
        
        return await host.to_dict(include_records=True)
    
    @staticmethod
    async def update_host(host_id: int, host_data: HostUpdate) -> Dict[str, Any]:
        """更新主机"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host:
            return None
        
        # 更新字段
        update_data = host_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(host, key, value)
        
        await host.save()
        return await host.to_dict()
    
    @staticmethod
    async def delete_host(host_id: int) -> bool:
        """删除主机"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host:
            return False
        
        # 删除关联的记录
        await MonitorHostRecord.filter(host_id=host_id).delete()
        await MonitorMRTGData.filter(host_id=host_id).delete()
        
        # 删除关联的服务
        services = await MonitorService.filter(host_id=host_id)
        for service in services:
            await MonitorServiceRecord.filter(service_id=service.id).delete()
        await MonitorService.filter(host_id=host_id).delete()
        
        # 删除主机
        await host.delete()
        return True
    
    @staticmethod
    async def ping_host(host_id: int) -> PingTestResult:
        """Ping测试主机"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host:
            return PingTestResult(
                success=False,
                message="主机不存在",
                data=None
            )
        
        # 执行ping命令
        try:
            # 根据操作系统类型选择适当的命令
            count_param = "-c"  # Linux/Unix
            cmd = f"ping {count_param} 4 -W 1 {host.ip}"
            
            # 执行命令并获取输出
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # 解析输出
            output = stdout.decode()
            
            # 检查是否有响应
            if "0 received" in output or "100% packet loss" in output:
                status = "offline"
                packet_loss = 100.0
                response_time = None
            else:
                status = "online"
                
                # 提取丢包率
                loss_match = re.search(r"(\d+)% packet loss", output)
                packet_loss = float(loss_match.group(1)) if loss_match else 0.0
                
                # 提取平均响应时间
                time_match = re.search(r"(?:rtt|round-trip).*?=.*?/(\d+\.\d+)/", output)
                response_time = int(float(time_match.group(1))) if time_match else None
            
            # 更新主机状态
            host.status = status
            if status == "online":
                host.last_online_time = datetime.datetime.now()
            await host.save()
            
            # 记录结果
            await MonitorHostRecord.create(
                host=host,
                status=status,
                response_time=response_time,
                packet_loss=packet_loss
            )
            
            # 返回结果
            return PingTestResult(
                success=True,
                message=f"Ping测试完成: {status}",
                data={
                    "status": status,
                    "response_time": response_time,
                    "packet_loss": packet_loss,
                    "raw_output": output
                }
            )
            
        except Exception as e:
            return PingTestResult(
                success=False,
                message=f"Ping测试失败: {str(e)}",
                data=None
            )
    
    @staticmethod
    async def _get_snmp_value(ip: str, community: str, oid: str, port: int = 161, timeout: int = 1) -> Any:
        """获取单个SNMP值（模拟实现）"""
        logger.info(f"模拟SNMP GET: {ip}:{port}, OID: {oid}")
        
        # 根据OID类型返回不同的模拟数据
        if "ifInOctets" in oid:
            return random.randint(1000000, 100000000)  # 入流量字节数
        elif "ifOutOctets" in oid:
            return random.randint(500000, 50000000)  # 出流量字节数
        elif "hrProcessorLoad" in oid:
            return random.randint(10, 90)  # CPU负载
        elif "memTotalReal" in oid:
            return 8 * 1024 * 1024  # 内存总量 (KB)
        elif "memAvailReal" in oid:
            return random.randint(2 * 1024 * 1024, 6 * 1024 * 1024)  # 可用内存 (KB)
        elif "dskPercent" in oid:
            return random.randint(20, 80)  # 磁盘使用率
        elif "sysUpTime" in oid:
            return "12345678"  # 系统运行时间
        elif "ifOperStatus" in oid:
            return 1  # 接口状态 (1=up)
        else:
            return None

    @staticmethod
    async def _get_snmp_walk(ip: str, community: str, oid: str, port: int = 161, timeout: int = 1) -> List[Dict[str, Any]]:
        """获取SNMP表数据（模拟实现）"""
        logger.info(f"模拟SNMP WALK: {ip}:{port}, OID: {oid}")
        
        result = []
        
        # 模拟不同类型的表数据
        if "ifTable" in oid:
            # 模拟3个网络接口
            for i in range(1, 4):
                result.append({
                    "oid": f"{SNMP_OIDS['ifIndex']}.{i}",
                    "index": str(i),
                    "value": i
                })
                result.append({
                    "oid": f"{SNMP_OIDS['ifDescr']}.{i}",
                    "index": str(i),
                    "value": f"eth{i-1}"
                })
                result.append({
                    "oid": f"{SNMP_OIDS['ifType']}.{i}",
                    "index": str(i),
                    "value": 6  # ethernet-csmacd
                })
                result.append({
                    "oid": f"{SNMP_OIDS['ifOperStatus']}.{i}",
                    "index": str(i),
                    "value": 1  # up
                })
        elif "dskTable" in oid:
            # 模拟2个磁盘
            for i in range(1, 3):
                result.append({
                    "oid": f"{SNMP_OIDS['dskPath']}.{i}",
                    "index": str(i),
                    "value": f"/dev/sda{i}"
                })
                result.append({
                    "oid": f"{SNMP_OIDS['dskTotal']}.{i}",
                    "index": str(i),
                    "value": 100 * 1024 * 1024  # 100GB
                })
                result.append({
                    "oid": f"{SNMP_OIDS['dskAvail']}.{i}",
                    "index": str(i),
                    "value": random.randint(20, 80) * 1024 * 1024  # 可用空间
                })
                result.append({
                    "oid": f"{SNMP_OIDS['dskPercent']}.{i}",
                    "index": str(i),
                    "value": random.randint(20, 80)  # 使用率
                })
        
        return result

    @staticmethod
    async def collect_host_snmp_data(host_id: int) -> Dict[str, Any]:
        """收集主机SNMP数据（改用模拟实现）"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host:
            return {"success": False, "message": "主机不存在"}
        
        if not host.enable_mrtg:
            return {"success": False, "message": "该主机未启用MRTG监控"}
        
        try:
            # 使用模拟数据替代真实SNMP数据
            logger.info(f"使用模拟数据收集主机 {host.host_name} ({host.ip}) 的SNMP数据")
            
            # 模拟数据
            result = {
                "in_traffic": random.uniform(10, 100),
                "out_traffic": random.uniform(5, 50),
                "cpu_usage": random.uniform(10, 90),
                "memory_usage": random.uniform(20, 80),
                "disk_usage": random.uniform(30, 70)
            }
            
            # 保存数据到数据库
            mrtg_data = await MonitorMRTGData.create(
                host=host,
                in_traffic=result["in_traffic"],
                out_traffic=result["out_traffic"],
                cpu_usage=result["cpu_usage"],
                memory_usage=result["memory_usage"],
                disk_usage=result["disk_usage"]
            )
            
            # 更新MRTG状态
            abnormal_threshold = 80  # 定义异常阈值为80%
            
            if (result["cpu_usage"] > abnormal_threshold or 
                result["memory_usage"] > abnormal_threshold or 
                result["disk_usage"] > abnormal_threshold):
                host.mrtg_status = "abnormal"
                
                # 创建告警
                await MonitorAlert.create(
                    level="warning",
                    target_type="host",
                    target_id=host.id,
                    target_name=host.host_name,
                    target_ip=host.ip,
                    alert_type="resource_usage",
                    content=f"主机 {host.host_name} 资源使用率超过阈值: " + 
                           (f"CPU {result['cpu_usage']}%, " if result["cpu_usage"] > abnormal_threshold else "") +
                           (f"内存 {result['memory_usage']}%, " if result["memory_usage"] > abnormal_threshold else "") +
                           (f"磁盘 {result['disk_usage']}%" if result["disk_usage"] > abnormal_threshold else ""),
                    details={
                        "cpu_usage": result["cpu_usage"],
                        "memory_usage": result["memory_usage"],
                        "disk_usage": result["disk_usage"],
                        "threshold": abnormal_threshold
                    }
                )
            else:
                host.mrtg_status = "normal"
            
            await host.save()
            
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"SNMP数据收集异常: {str(e)}")
            # 设置状态异常
            host.mrtg_status = "abnormal"
            await host.save()
            return {"success": False, "message": f"SNMP数据收集异常: {str(e)}"}

    @staticmethod
    async def generate_mock_mrtg_data(host_id: int) -> Dict[str, Any]:
        """生成模拟的MRTG数据（仅用于演示）"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host or not host.enable_mrtg:
            return None
        
        # 直接使用模拟数据
        logger.info(f"生成模拟数据，主机ID: {host_id}")
        
        # 模拟数据
        result = {
            "in_traffic": random.uniform(10, 100),
            "out_traffic": random.uniform(5, 50),
            "cpu_usage": random.uniform(10, 90),
            "memory_usage": random.uniform(20, 80),
            "disk_usage": random.uniform(30, 70),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 创建MRTG数据
        mrtg_data = await MonitorMRTGData.create(
            host=host,
            in_traffic=result["in_traffic"],
            out_traffic=result["out_traffic"],
            cpu_usage=result["cpu_usage"],
            memory_usage=result["memory_usage"],
            disk_usage=result["disk_usage"]
        )
        
        # 更新MRTG状态
        abnormal_threshold = 80  # 定义异常阈值为80%
        
        if (result["cpu_usage"] > abnormal_threshold or 
            result["memory_usage"] > abnormal_threshold or 
            result["disk_usage"] > abnormal_threshold):
            host.mrtg_status = "abnormal"
            
            # 创建告警
            await MonitorAlert.create(
                level="warning",
                target_type="host",
                target_id=host.id,
                target_name=host.host_name,
                target_ip=host.ip,
                alert_type="resource_usage",
                content=f"主机 {host.host_name} 资源使用率超过阈值: " + 
                       (f"CPU {result['cpu_usage']}%, " if result["cpu_usage"] > abnormal_threshold else "") +
                       (f"内存 {result['memory_usage']}%, " if result["memory_usage"] > abnormal_threshold else "") +
                       (f"磁盘 {result['disk_usage']}%" if result["disk_usage"] > abnormal_threshold else ""),
                details={
                    "cpu_usage": result["cpu_usage"],
                    "memory_usage": result["memory_usage"],
                    "disk_usage": result["disk_usage"],
                    "threshold": abnormal_threshold
                }
            )
        else:
            host.mrtg_status = "normal"
        
        await host.save()
        
        return {"success": True, "data": result}

    @staticmethod
    async def get_mrtg_data(host_id: int, days: int = 1) -> List[Dict[str, Any]]:
        """获取MRTG数据"""
        host = await MonitorHost.get_or_none(id=host_id)
        if not host or not host.enable_mrtg:
            return []
        
        # 计算时间范围
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=days)
        
        # 查询数据
        mrtg_data = await MonitorMRTGData.filter(
            host_id=host_id,
            created_at__gte=start_time,
            created_at__lte=end_time
        ).order_by("created_at")
        
        # 转换为前端所需格式
        result = []
        for data in mrtg_data:
            # 格式化数据
            result.append({
                "id": data.id,
                "host_id": data.host_id,
                "timestamp": data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "inbound_traffic": round(data.in_traffic, 2),
                "outbound_traffic": round(data.out_traffic, 2),
                "cpu_usage": round(data.cpu_usage, 2),
                "memory_usage": round(data.memory_usage, 2),
                "disk_usage": round(data.disk_usage, 2)
            })
        
        return result

    # 服务监控相关方法
    @staticmethod
    async def get_service_list(
        page: int = 1, 
        page_size: int = 10, 
        service_name: Optional[str] = None,
        url: Optional[str] = None,
        status: Optional[str] = None,
        service_type: Optional[str] = None,
        host_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取服务列表"""
        # 构建查询条件
        query = {}
        if service_name:
            query["service_name__contains"] = service_name
        if url:
            query["url__contains"] = url
        if status:
            query["status"] = status
        if service_type:
            query["service_type"] = service_type
        if host_id:
            query["host_id"] = host_id
            
        # 查询总数
        total = await MonitorService.filter(**query).count()
        
        # 分页查询
        services = await MonitorService.filter(**query).offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        service_list = [await service.to_dict() for service in services]
        
        return {
            "items": service_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_service(service_data: ServiceCreate) -> Dict[str, Any]:
        """创建服务"""
        # 验证主机ID是否存在
        if service_data.host_id:
            host = await MonitorHost.get_or_none(id=service_data.host_id)
            if not host:
                return None
        
        service = await MonitorService.create(
            service_name=service_data.service_name,
            url=service_data.url,
            service_type=service_data.service_type,
            check_method=service_data.check_method,
            expected_status=service_data.expected_status,
            check_interval=service_data.check_interval,
            timeout=service_data.timeout,
            host_id=service_data.host_id,
            remark=service_data.remark
        )
        
        # 创建时进行一次服务检测
        check_result = await MonitorController.check_service(service.id)
        
        return await service.to_dict()
    
    @staticmethod
    async def get_service(service_id: int) -> Dict[str, Any]:
        """获取服务详情"""
        service = await MonitorService.get_or_none(id=service_id)
        if not service:
            return None
        
        return await service.to_dict(include_records=True)
    
    @staticmethod
    async def update_service(service_id: int, service_data: ServiceUpdate) -> Dict[str, Any]:
        """更新服务"""
        service = await MonitorService.get_or_none(id=service_id)
        if not service:
            return None
        
        # 验证主机ID是否存在
        if service_data.host_id:
            host = await MonitorHost.get_or_none(id=service_data.host_id)
            if not host:
                return None
        
        # 更新字段
        update_data = service_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)
        
        await service.save()
        return await service.to_dict()
    
    @staticmethod
    async def delete_service(service_id: int) -> bool:
        """删除服务"""
        service = await MonitorService.get_or_none(id=service_id)
        if not service:
            return False
        
        # 删除关联的记录
        await MonitorServiceRecord.filter(service_id=service_id).delete()
        
        # 删除服务
        await service.delete()
        return True
    
    @staticmethod
    async def check_service(service_id: int) -> ServiceTestResult:
        """检测服务"""
        service = await MonitorService.get_or_none(id=service_id)
        if not service:
            return ServiceTestResult(
                success=False,
                message="服务不存在",
                data=None
            )
        
        # 根据检测方法执行检测
        try:
            status_code = None
            response_time = None
            content = None
            status = "unknown"
            start_time = datetime.datetime.now()
            
            if service.check_method == "http_get":
                # 执行HTTP GET请求
                async with aiohttp.ClientSession() as session:
                    async with session.get(service.url, timeout=service.timeout) as response:
                        end_time = datetime.datetime.now()
                        response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒
                        status_code = response.status
                        content = await response.text()
                        
                        # 判断状态
                        if str(status_code) == service.expected_status:
                            status = "normal"
                        else:
                            status = "error"
            
            elif service.check_method == "http_post":
                # 执行HTTP POST请求
                async with aiohttp.ClientSession() as session:
                    async with session.post(service.url, timeout=service.timeout) as response:
                        end_time = datetime.datetime.now()
                        response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒
                        status_code = response.status
                        content = await response.text()
                        
                        # 判断状态
                        if str(status_code) == service.expected_status:
                            status = "normal"
                        else:
                            status = "error"
            
            elif service.check_method == "ping":
                # 执行Ping检测
                cmd = f"ping -c 4 -W 1 {service.url}"
                
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                end_time = datetime.datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒
                output = stdout.decode()
                content = output
                
                # 检查是否有响应
                if "0 received" in output or "100% packet loss" in output:
                    status = "error"
                else:
                    status = "normal"
                    
                    # 提取平均响应时间
                    time_match = re.search(r"(?:rtt|round-trip).*?=.*?/(\d+\.\d+)/", output)
                    if time_match:
                        response_time = int(float(time_match.group(1)))
            
            elif service.check_method == "tcp":
                # 执行TCP连接检测
                import socket
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(service.timeout)
                
                host, port = service.url.split(":")
                s.connect((host, int(port)))
                
                end_time = datetime.datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # 毫秒
                s.close()
                
                status = "normal"
                content = "TCP连接成功"
            
            # 更新服务状态
            service.status = status
            service.last_response_time = response_time
            service.last_check_time = datetime.datetime.now()
            await service.save()
            
            # 记录结果
            record = await MonitorServiceRecord.create(
                service=service,
                status=status,
                response_time=response_time,
                status_code=status_code,
                content=content[:1000] if content else None  # 限制内容长度
            )
            
            # 如果状态是error，创建告警
            if status == "error" and not content:
                await MonitorAlert.create(
                    level="error",
                    target_type="service",
                    target_id=service.id,
                    target_name=service.service_name,
                    target_ip=None,
                    alert_type="service_unavailable",
                    content=f"服务不可用: {service.service_name} ({service.url})",
                    details={
                        "url": service.url,
                        "check_method": service.check_method,
                        "response_time": response_time,
                        "status_code": status_code
                    }
                )
            
            # 返回结果
            return ServiceTestResult(
                success=True,
                message=f"服务检测完成: {status}",
                data={
                    "status": status,
                    "response_time": response_time,
                    "status_code": status_code,
                    "content": content[:1000] if content else None
                }
            )
            
        except Exception as e:
            # 更新服务状态
            service.status = "error"
            service.last_check_time = datetime.datetime.now()
            await service.save()
            
            # 记录结果
            await MonitorServiceRecord.create(
                service=service,
                status="error",
                response_time=None,
                status_code=None,
                content=str(e)
            )
            
            # 创建告警
            await MonitorAlert.create(
                level="error",
                target_type="service",
                target_id=service.id,
                target_name=service.service_name,
                target_ip=None,
                alert_type="service_error",
                content=f"服务检测异常: {service.service_name} ({service.url})",
                details={
                    "url": service.url,
                    "check_method": service.check_method,
                    "error": str(e)
                }
            )
            
            logger.error(f"监控服务 {service.service_name} 时发生异常: {str(e)}")
            return ServiceTestResult(
                success=False,
                message=f"服务检测失败: {str(e)}",
                data=None
            )
    
    @staticmethod
    async def get_service_history(service_id: int, days: int = 1) -> List[Dict[str, Any]]:
        """获取服务响应时间历史"""
        service = await MonitorService.get_or_none(id=service_id)
        if not service:
            return []
        
        # 计算时间范围
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=days)
        
        # 查询数据
        records = await MonitorServiceRecord.filter(
            service_id=service_id,
            created_at__gte=start_time,
            created_at__lte=end_time
        ).order_by("created_at")
        
        # 转换为字典
        return [await record.to_dict() for record in records]
    
    # 监控面板相关方法
    @staticmethod
    async def get_dashboard_data() -> DashboardData:
        """获取监控面板数据"""
        # 获取主机和服务数量
        host_count = await MonitorHost.all().count()
        service_count = await MonitorService.all().count()
        
        # 获取在线主机数和正常服务数
        online_host_count = await MonitorHost.filter(status="online").count()
        normal_service_count = await MonitorService.filter(status="normal").count()
        
        # 获取告警数量
        alert_count = await MonitorAlert.all().count()
        unresolved_alert_count = await MonitorAlert.filter(resolved=False).count()
        
        # 获取主机状态分布
        host_status_query = await MonitorHost.all().values_list("status", flat=True)
        host_status_distribution = {}
        for status in host_status_query:
            if status in host_status_distribution:
                host_status_distribution[status] += 1
            else:
                host_status_distribution[status] = 1
        
        # 获取服务状态分布
        service_status_query = await MonitorService.all().values_list("status", flat=True)
        service_status_distribution = {}
        for status in service_status_query:
            if status in service_status_distribution:
                service_status_distribution[status] += 1
            else:
                service_status_distribution[status] = 1
        
        # 获取告警级别分布
        alert_level_query = await MonitorAlert.all().values_list("level", flat=True)
        alert_level_distribution = {}
        for level in alert_level_query:
            if level in alert_level_distribution:
                alert_level_distribution[level] += 1
            else:
                alert_level_distribution[level] = 1
        
        # 获取最近告警
        recent_alerts = await MonitorAlert.all().order_by("-created_at").limit(10)
        recent_alerts_data = [await alert.to_dict() for alert in recent_alerts]
        
        return DashboardData(
            host_count=host_count,
            service_count=service_count,
            online_host_count=online_host_count,
            normal_service_count=normal_service_count,
            alert_count=alert_count,
            unresolved_alert_count=unresolved_alert_count,
            host_status_distribution=host_status_distribution,
            service_status_distribution=service_status_distribution,
            alert_level_distribution=alert_level_distribution,
            recent_alerts=recent_alerts_data
        )
    
    # 告警相关方法
    @staticmethod
    async def get_alert_list(
        page: int = 1, 
        page_size: int = 10, 
        level: Optional[str] = None,
        target_type: Optional[str] = None,
        resolved: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取告警列表"""
        # 构建查询条件
        query = {}
        if level:
            query["level"] = level
        if target_type:
            query["target_type"] = target_type
        if resolved is not None:
            query["resolved"] = resolved
            
        # 查询总数
        total = await MonitorAlert.filter(**query).count()
        
        # 分页查询
        alerts = await MonitorAlert.filter(**query).order_by("-created_at").offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        alert_list = [await alert.to_dict() for alert in alerts]
        
        return {
            "items": alert_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def get_alert(alert_id: int) -> Dict[str, Any]:
        """获取告警详情"""
        alert = await MonitorAlert.get_or_none(id=alert_id)
        if not alert:
            return None
        
        return await alert.to_dict()
    
    @staticmethod
    async def update_alert(alert_id: int, alert_data: AlertUpdate) -> Dict[str, Any]:
        """更新告警"""
        alert = await MonitorAlert.get_or_none(id=alert_id)
        if not alert:
            return None
        
        # 更新字段
        alert.resolved = alert_data.resolved
        if alert_data.resolved:
            alert.resolved_at = datetime.datetime.now()
        
        await alert.save()
        return await alert.to_dict() 
import asyncio
import datetime
from typing import Dict, List, Any

from app.models.monitor import MonitorHost, MonitorService
from app.controllers.monitor import MonitorController
from app.log import logger

# 计划任务运行标记
tasks_running = {
    "monitor_hosts": False,
    "monitor_services": False
}

async def start_monitor_tasks():
    """启动所有监控任务"""
    logger.info("启动监控任务调度器")
    
    # 启动主机监控任务
    asyncio.create_task(schedule_host_monitor())
    
    # 启动服务监控任务
    asyncio.create_task(schedule_service_monitor())
    
    logger.info("监控任务调度器已启动")

async def schedule_host_monitor():
    """调度主机监控任务"""
    global tasks_running
    
    if tasks_running["monitor_hosts"]:
        logger.warning("主机监控任务已在运行中")
        return
    
    tasks_running["monitor_hosts"] = True
    
    try:
        while True:
            # 获取所有启用MRTG的主机
            hosts = await MonitorHost.filter(enable_mrtg=True)
            logger.info(f"开始对 {len(hosts)} 台主机进行SNMP监控")
            
            # 为每个主机创建监控任务
            for host in hosts:
                try:
                    # 检查是否需要收集数据
                    current_time = datetime.datetime.now()
                    # 这里可以根据主机的ping_interval来确定收集频率
                    # 默认每60秒收集一次
                    
                    logger.info(f"收集主机 {host.host_name} ({host.ip}) 的SNMP数据")
                    result = await MonitorController.collect_host_snmp_data(host.id)
                    
                    if result["success"]:
                        logger.info(f"成功收集主机 {host.host_name} 的SNMP数据")
                    else:
                        logger.warning(f"收集主机 {host.host_name} 的SNMP数据失败: {result.get('message', '未知错误')}")
                
                except Exception as e:
                    logger.error(f"监控主机 {host.host_name} 时发生异常: {str(e)}")
            
            # 等待60秒
            await asyncio.sleep(60)
    
    except asyncio.CancelledError:
        logger.info("主机监控任务被取消")
    except Exception as e:
        logger.error(f"主机监控任务异常: {str(e)}")
    finally:
        tasks_running["monitor_hosts"] = False

async def schedule_service_monitor():
    """调度服务监控任务"""
    global tasks_running
    
    if tasks_running["monitor_services"]:
        logger.warning("服务监控任务已在运行中")
        return
    
    tasks_running["monitor_services"] = True
    
    try:
        while True:
            # 获取所有服务
            services = await MonitorService.all()
            logger.info(f"开始对 {len(services)} 个服务进行监控")
            
            # 为每个服务创建监控任务
            for service in services:
                try:
                    # 检查是否需要检测服务
                    current_time = datetime.datetime.now()
                    # 修复时间比较问题，确保两个时间对象有相同的时区信息
                    if service.last_check_time is None:
                        need_check = True
                    else:
                        # 确保时间对象比较是兼容的
                        if hasattr(service.last_check_time, 'tzinfo') and service.last_check_time.tzinfo is not None:
                            # 如果last_check_time有tzinfo，给current_time也添加相同的时区
                            current_time = current_time.replace(tzinfo=service.last_check_time.tzinfo)
                        else:
                            # 如果last_check_time没有tzinfo，确保current_time也没有
                            if hasattr(current_time, 'tzinfo') and current_time.tzinfo is not None:
                                current_time = current_time.replace(tzinfo=None)
                        
                        # 如果上次检测时间 + 检测间隔 < 当前时间，则需要检测
                        need_check = (service.last_check_time + 
                                     datetime.timedelta(seconds=service.check_interval)) < current_time
                    
                    if need_check:
                        logger.info(f"检测服务 {service.service_name} ({service.url})")
                        result = await MonitorController.check_service(service.id)
                        
                        if result.success:
                            logger.info(f"成功检测服务 {service.service_name}")
                        else:
                            logger.warning(f"检测服务 {service.service_name} 失败: {result.message}")
                
                except Exception as e:
                    logger.error(f"监控服务 {service.service_name} 时发生异常: {str(e)}")
            
            # 等待30秒
            await asyncio.sleep(30)
    
    except asyncio.CancelledError:
        logger.info("服务监控任务被取消")
    except Exception as e:
        logger.error(f"服务监控任务异常: {str(e)}")
    finally:
        tasks_running["monitor_services"] = False

# 停止所有任务
async def stop_monitor_tasks():
    """停止所有监控任务"""
    global tasks_running
    
    logger.info("停止监控任务")
    
    tasks_running["monitor_hosts"] = False
    tasks_running["monitor_services"] = False
    
    # 等待任务结束
    await asyncio.sleep(1)
    
    logger.info("监控任务已停止") 
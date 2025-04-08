from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas import Success
import psutil
import os
import platform
import subprocess
import re

router = APIRouter()

@router.get("/processes", summary="进程列表")
async def list_processes(
    name: Optional[str] = Query(None, description="进程名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量")
):
    """获取进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                process_info = proc.info()
                if name and name.lower() not in process_info['name'].lower():
                    continue
                processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        total = len(processes)
        processes = processes[start:end]
        
        return Success(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "processes": processes
        })
    except Exception as e:
        return Success(code=400, msg="获取进程列表失败", data={"error": str(e)})

@router.get("/resources", summary="系统资源")
async def get_resources():
    """获取系统资源使用情况"""
    try:
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # 内存信息
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 磁盘信息
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except Exception:
                continue
        
        # 网络信息
        net_io = psutil.net_io_counters()
        
        return Success(data={
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": cpu_freq.min if cpu_freq else None,
                    "max": cpu_freq.max if cpu_freq else None
                }
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            },
            "disks": disks,
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        })
    except Exception as e:
        return Success(code=400, msg="获取系统资源失败", data={"error": str(e)})

@router.get("/services", summary="系统服务")
async def list_services(
    name: Optional[str] = Query(None, description="服务名称")
):
    """获取系统服务列表"""
    try:
        if platform.system().lower() == "windows":
            # Windows系统使用sc命令
            cmd = ["sc", "query"]
            if name:
                cmd.append(name)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return Success(code=400, msg="获取服务列表失败", data={"error": stderr.decode()})
            
            # 解析Windows服务列表
            services = []
            current_service = {}
            for line in stdout.decode().split("\n"):
                line = line.strip()
                if line.startswith("SERVICE_NAME"):
                    if current_service:
                        services.append(current_service)
                    current_service = {"name": line.split(":")[1].strip()}
                elif line.startswith("STATE"):
                    state = line.split(":")[1].strip()
                    current_service["state"] = state
                elif line.startswith("TYPE"):
                    type_ = line.split(":")[1].strip()
                    current_service["type"] = type_
            
            if current_service:
                services.append(current_service)
        else:
            # Linux/Unix系统使用systemctl命令
            cmd = ["systemctl", "list-units", "--type=service", "--all"]
            if name:
                cmd.extend(["--pattern", name])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return Success(code=400, msg="获取服务列表失败", data={"error": stderr.decode()})
            
            # 解析Linux服务列表
            services = []
            for line in stdout.decode().split("\n"):
                if line.strip() and not line.startswith("UNIT"):
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            "name": parts[0],
                            "load": parts[1],
                            "active": parts[2],
                            "sub": parts[3],
                            "description": " ".join(parts[4:])
                        })
        
        return Success(data={"services": services})
    except Exception as e:
        return Success(code=400, msg="获取服务列表失败", data={"error": str(e)})

@router.get("/logs", summary="系统日志")
async def get_logs(
    log_type: str = Query("system", description="日志类型：system, auth, application"),
    lines: int = Query(100, description="获取行数")
):
    """获取系统日志"""
    try:
        if platform.system().lower() == "windows":
            # Windows系统使用Get-EventLog命令
            cmd = ["powershell", "-Command", f"Get-EventLog -LogName {log_type} -Newest {lines} | ConvertTo-Json"]
        else:
            # Linux/Unix系统使用journalctl命令
            cmd = ["journalctl", "-n", str(lines)]
            if log_type == "system":
                cmd.append("--system")
            elif log_type == "auth":
                cmd.append("--auth")
            elif log_type == "application":
                cmd.append("--user")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return Success(code=400, msg="获取系统日志失败", data={"error": stderr.decode()})
        
        return Success(data={
            "type": log_type,
            "lines": lines,
            "content": stdout.decode()
        })
    except Exception as e:
        return Success(code=400, msg="获取系统日志失败", data={"error": str(e)}) 
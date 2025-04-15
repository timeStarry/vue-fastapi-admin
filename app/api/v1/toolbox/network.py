from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas import Success
import asyncio
import socket
import dns.resolver
import subprocess
import platform
import re

router = APIRouter()

@router.post("/ping", summary="Ping测试")
async def ping_test(
    host: str = Query(..., description="目标主机"),
    count: int = Query(4, description="发送次数"),
    timeout: float = Query(1.0, description="超时时间(秒)")
):
    """执行Ping测试"""
    try:
        # 根据操作系统选择ping命令参数
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        
        # 执行ping命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return Success(code=400, msg="Ping测试失败", data={
                "host": host,
                "error": stderr.decode()
            })
        
        # 解析ping结果
        result = stdout.decode()
        if platform.system().lower() == "windows":
            # Windows ping结果解析
            sent = re.search(r"已发送 = (\d+)", result)
            received = re.search(r"已接收 = (\d+)", result)
            lost = re.search(r"丢失 = (\d+)", result)
            times = re.findall(r"时间=(\d+)ms", result)
        else:
            # Linux/Unix ping结果解析
            sent = re.search(r"(\d+) packets transmitted", result)
            received = re.search(r"(\d+) received", result)
            lost = re.search(r"(\d+)% packet loss", result)
            times = re.findall(r"time=([\d.]+) ms", result)
        
        return Success(data={
            "host": host,
            "sent": int(sent.group(1)) if sent else 0,
            "received": int(received.group(1)) if received else 0,
            "lost": int(lost.group(1)) if lost else 0,
            "times": [float(t) for t in times],
            "raw": result
        })
    except Exception as e:
        return Success(code=400, msg="Ping测试失败", data={"error": str(e)})

@router.post("/port-scan", summary="端口扫描")
async def port_scan(
    host: str = Query(..., description="目标主机"),
    ports: str = Query("80,443,22,21,3306,6379", description="要扫描的端口，多个端口用逗号分隔"),
    timeout: float = Query(1.0, description="超时时间(秒)"),
):
    """执行端口扫描"""
    try:
        port_list = [int(p.strip()) for p in ports.split(",")]
        results = []
        
        for port in port_list:
            try:
                # 创建socket连接
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                # 尝试连接
                result = sock.connect_ex((host, port))
                sock.close()
                
                results.append({
                    "port": port,
                    "status": "open" if result == 0 else "closed",
                    "error": None if result == 0 else f"错误代码: {result}"
                })
            except Exception as e:
                results.append({
                    "port": port,
                    "status": "error",
                    "error": str(e)
                })
        
        return Success(data={
            "host": host,
            "results": results
        })
    except Exception as e:
        return Success(code=400, msg="端口扫描失败", data={"error": str(e)})

@router.post("/dns-query", summary="DNS查询")
async def dns_query(
    domain: str = Query(..., description="域名"),
    record_type: str = Query("A", description="记录类型：A, AAAA, CNAME, MX, TXT, NS"),
):
    """执行DNS查询"""
    try:
        # 创建DNS解析器
        resolver = dns.resolver.Resolver()
        
        # 执行查询
        answers = resolver.resolve(domain, record_type)
        
        # 处理查询结果
        results = []
        for rdata in answers:
            if record_type == "A":
                results.append({"type": "A", "value": str(rdata)})
            elif record_type == "AAAA":
                results.append({"type": "AAAA", "value": str(rdata)})
            elif record_type == "CNAME":
                results.append({"type": "CNAME", "value": str(rdata)})
            elif record_type == "MX":
                results.append({
                    "type": "MX",
                    "preference": rdata.preference,
                    "value": str(rdata.exchange)
                })
            elif record_type == "TXT":
                results.append({"type": "TXT", "value": str(rdata)})
            elif record_type == "NS":
                results.append({"type": "NS", "value": str(rdata)})
        
        return Success(data={
            "domain": domain,
            "record_type": record_type,
            "results": results
        })
    except Exception as e:
        return Success(code=400, msg="DNS查询失败", data={"error": str(e)})

@router.post("/traceroute", summary="路由追踪")
async def traceroute(
    host: str = Query(..., description="目标主机"),
    max_hops: int = Query(30, description="最大跳数"),
    timeout: float = Query(1.0, description="超时时间(秒)"),
):
    """执行路由追踪"""
    try:
        if platform.system().lower() == "windows":
            # Windows 使用 tracert 命令
            cmd = ["tracert", "-h", str(max_hops), "-w", str(int(timeout * 1000)), host]
        else:
            # Linux/Unix 使用 traceroute 命令
            cmd = ["traceroute", "-m", str(max_hops), "-w", str(timeout), host]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Traceroute failed: {stderr.decode()}")
        
        # 解析输出结果
        hops = []
        for line in stdout.decode().split("\n"):
            if line.strip():
                if platform.system().lower() == "windows":
                    # Windows tracert 输出格式解析
                    match = re.match(r"\s*(\d+)\s+(\d+ ms)\s+(\d+ ms)\s+(\d+ ms)\s+(.*)", line)
                    if match:
                        hop_num, t1, t2, t3, ip = match.groups()
                        hops.append({
                            "hop": int(hop_num),
                            "ip": ip.strip(),
                            "times": [t1, t2, t3]
                        })
                else:
                    # Linux traceroute 输出格式解析
                    match = re.match(r"\s*(\d+)\s+(.*?)\s+(\d+\.\d+ ms)", line)
                    if match:
                        hop_num, ip, time = match.groups()
                        hops.append({
                            "hop": int(hop_num),
                            "ip": ip.strip(),
                            "times": [time]
                        })
        
        return Success(data={
            "host": host,
            "max_hops": max_hops,
            "timeout": timeout,
            "hops": hops
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
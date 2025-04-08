from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas import Success
import re
import hashlib
import socket
import ssl
import OpenSSL
import requests
from datetime import datetime

router = APIRouter()

@router.post("/password-check", summary="密码强度检查")
async def check_password(
    password: str = Query(..., description="密码")
):
    """检查密码强度"""
    try:
        score = 0
        feedback = []
        
        # 长度检查
        if len(password) < 8:
            feedback.append("密码长度至少为8个字符")
        else:
            score += 1
        
        # 包含数字
        if not re.search(r"\d", password):
            feedback.append("密码应包含数字")
        else:
            score += 1
        
        # 包含小写字母
        if not re.search(r"[a-z]", password):
            feedback.append("密码应包含小写字母")
        else:
            score += 1
        
        # 包含大写字母
        if not re.search(r"[A-Z]", password):
            feedback.append("密码应包含大写字母")
        else:
            score += 1
        
        # 包含特殊字符
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            feedback.append("密码应包含特殊字符")
        else:
            score += 1
        
        # 计算密码强度
        strength = "弱"
        if score >= 4:
            strength = "强"
        elif score >= 3:
            strength = "中"
        
        return Success(data={
            "score": score,
            "strength": strength,
            "feedback": feedback
        })
    except Exception as e:
        return Success(code=400, msg="密码强度检查失败", data={"error": str(e)})

@router.post("/ssl-check", summary="SSL证书检查")
async def check_ssl(
    domain: str = Query(..., description="域名"),
    port: int = Query(443, description="端口")
):
    """检查SSL证书状态"""
    try:
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 连接服务器
        with socket.create_connection((domain, port)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # 获取证书信息
                not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                
                # 检查证书是否过期
                now = datetime.now()
                is_expired = now > not_after
                days_until_expiry = (not_after - now).days
                
                # 检查证书链
                cert_chain = []
                for cert in cert.get('issuer', []):
                    cert_chain.append({
                        'name': cert.get('organizationName', ''),
                        'country': cert.get('countryName', '')
                    })
                
                return Success(data={
                    "domain": domain,
                    "port": port,
                    "issuer": cert.get('issuer', []),
                    "subject": cert.get('subject', []),
                    "version": cert.get('version', ''),
                    "serial_number": cert.get('serialNumber', ''),
                    "not_before": not_before.isoformat(),
                    "not_after": not_after.isoformat(),
                    "is_expired": is_expired,
                    "days_until_expiry": days_until_expiry,
                    "cert_chain": cert_chain
                })
    except Exception as e:
        return Success(code=400, msg="SSL证书检查失败", data={"error": str(e)})

@router.post("/headers-check", summary="HTTP头检查")
async def check_headers(
    url: str = Query(..., description="URL")
):
    """检查HTTP安全头"""
    try:
        # 发送请求
        response = requests.get(url, verify=False)
        headers = dict(response.headers)
        
        # 检查安全头
        security_headers = {
            "X-Frame-Options": headers.get("X-Frame-Options", "未设置"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options", "未设置"),
            "X-XSS-Protection": headers.get("X-XSS-Protection", "未设置"),
            "Strict-Transport-Security": headers.get("Strict-Transport-Security", "未设置"),
            "Content-Security-Policy": headers.get("Content-Security-Policy", "未设置"),
            "Referrer-Policy": headers.get("Referrer-Policy", "未设置"),
            "Permissions-Policy": headers.get("Permissions-Policy", "未设置")
        }
        
        # 分析安全头状态
        analysis = {}
        for header, value in security_headers.items():
            if value == "未设置":
                analysis[header] = {
                    "status": "warning",
                    "message": f"{header} 未设置，建议配置"
                }
            else:
                analysis[header] = {
                    "status": "success",
                    "message": f"{header} 已设置"
                }
        
        return Success(data={
            "url": url,
            "status_code": response.status_code,
            "security_headers": security_headers,
            "analysis": analysis
        })
    except Exception as e:
        return Success(code=400, msg="HTTP头检查失败", data={"error": str(e)})

@router.post("/hash-check", summary="哈希值检查")
async def check_hash(
    text: str = Query(..., description="文本内容")
):
    """计算文本的哈希值"""
    try:
        # 计算不同算法的哈希值
        hashes = {
            "md5": hashlib.md5(text.encode()).hexdigest(),
            "sha1": hashlib.sha1(text.encode()).hexdigest(),
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "sha512": hashlib.sha512(text.encode()).hexdigest()
        }
        
        return Success(data={
            "text": text,
            "hashes": hashes
        })
    except Exception as e:
        return Success(code=400, msg="哈希值计算失败", data={"error": str(e)}) 
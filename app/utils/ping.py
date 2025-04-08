import platform
import subprocess
from typing import Tuple

async def ping_host(hostname: str) -> Tuple[bool, str]:
    """
    Ping主机检测是否可达
    
    Args:
        hostname: 主机名或IP地址
        
    Returns:
        Tuple[bool, str]: (是否可达, 消息)
    """
    # 根据操作系统选择ping命令参数
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', '1', '-w', '1000', hostname]  # Windows: -w 以毫秒为单位
    else:
        command = ['ping', '-c', '1', '-W', '1', hostname]     # Linux/Unix: -W 以秒为单位
    
    try:
        # 执行ping命令
        result = subprocess.run(command, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True,  # 返回文本而不是字节
                              timeout=3)  # 进程超时时间
        
        if result.returncode == 0:
            return True, "Host is reachable"
        else:
            # 返回具体的错误信息
            error_msg = result.stderr or result.stdout or "Host is unreachable"
            return False, error_msg.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Ping process timeout"
    except Exception as e:
        return False, f"Error: {str(e)}" 
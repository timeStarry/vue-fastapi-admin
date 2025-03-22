import asyncio
import asyncssh
from typing import Tuple

async def test_ssh_connection(
    hostname: str,
    port: int,
    username: str,
    password: str = None,
    private_key: str = None
) -> Tuple[bool, str]:
    """测试SSH连接"""
    #TODO: 不推荐用户采用密码认证
    try:
        if private_key:
            key = asyncssh.import_private_key(private_key)
            conn = await asyncssh.connect(
                hostname,
                port=port,
                username=username,
                client_keys=[key],
                known_hosts=None
            )
        else:
            conn = await asyncssh.connect(
                hostname,
                port=port,
                username=username,
                password=password,
                known_hosts=None
            )
        
        conn.close()
        return True, "连接成功"
    except (asyncssh.Error, OSError) as exc:
        return False, f"连接失败: {str(exc)}" 
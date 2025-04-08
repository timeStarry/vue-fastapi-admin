import os
import typing
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str
    PROJECT_NAME: str
    APP_DESCRIPTION: str
    DEBUG: bool

    # 安全配置
    SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    # 数据库配置
    DB_ENGINE: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int

    # CORS配置
    CORS_ORIGINS: typing.List[str]
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: typing.List[str]
    CORS_ALLOW_HEADERS: typing.List[str]

    # 路径配置
    ROOT_DIR: Path = Path(__file__).parent.parent.parent  # 指向项目根目录
    APP_DIR: Path = ROOT_DIR / "app"
    LOGS_DIR: Path = APP_DIR / "logs"

    # 时区配置
    TIMEZONE: str = "Asia/Shanghai"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOGS_ROOT: str = "app/logs"

    # 构建 TORTOISE_ORM 配置
    @property
    def TORTOISE_ORM(self) -> dict:
        return {
            "connections": {
                "default": {
                    "engine": self.DB_ENGINE,
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_NAME,
                    },
                },
            },
            "apps": {
                "models": {
                    "models": [
                        "app.models.user",
                        "app.models.role",
                        "app.models.menu",
                        "app.models.api",
                        "aerich.models"
                    ],
                    "default_connection": "default",
                },
            },
            "use_tz": False,
            "timezone": self.TIMEZONE,
        }

    class Config:
        # 使用字符串路径或直接计算路径
        env_file = str(Path(__file__).parent.parent.parent / ".env")  # 明确指定 .env 文件位置
        case_sensitive = True


settings = Settings()

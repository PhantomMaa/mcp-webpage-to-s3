"""配置管理模块"""

import os
from typing import Optional, Literal
from pydantic import BaseModel, Field
import yaml
from pathlib import Path


class S3Config(BaseModel):
    """S3 云存储配置"""

    access_key: str = Field(description="访问密钥 ID")
    secret_key: str = Field(description="访问密钥")
    endpoint: Optional[str] = Field(default=None, description="存储服务端点")
    region: Optional[str] = Field(default=None, description="存储区域")
    bucket: str = Field(description="存储桶名称")
    base_url: str = Field(default="", description="基础 URL 前缀")

    @classmethod
    def from_env(cls) -> Optional['S3Config']:
        """从环境变量创建 S3 配置"""
        access_key = os.getenv('MCP_S3_ACCESS_KEY')
        secret_key = os.getenv('MCP_S3_SECRET_KEY')
        bucket = os.getenv('MCP_S3_BUCKET')
        
        if not all([access_key, secret_key, bucket]):
            return None
            
        return cls(
            access_key=access_key,  # type: ignore
            secret_key=secret_key,  # type: ignore
            endpoint=os.getenv('MCP_S3_ENDPOINT'),
            region=os.getenv('MCP_S3_REGION'),
            bucket=bucket,  # type: ignore
            base_url=os.getenv('MCP_S3_BASE_URL', '')
        )


class MCPServerConfig(BaseModel):
    """MCP 服务器配置"""

    transport: Literal["stdio", "http", "sse", "streamable-http"] = Field(default="stdio", description="传输协议：stdio, http, sse, streamable-http")
    port: int = Field(default=8000, description="MCP 服务器端口")

    @classmethod
    def from_env(cls) -> 'MCPServerConfig':
        """从环境变量创建 MCP 服务器配置"""
        transport_str = os.getenv('MCP_TRANSPORT', 'stdio')
        # 验证 transport 值
        valid_transports = ["stdio", "http", "sse", "streamable-http"]
        transport = transport_str if transport_str in valid_transports else "stdio"
        port = int(os.getenv('MCP_PORT', '8000'))
        
        return cls(transport=transport, port=port)  # type: ignore


class ServerConfig(BaseModel):
    """MCP 服务器配置"""

    s3: S3Config
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    log_level: str = Field(default="INFO", description="日志级别")


def load_config_from_file() -> ServerConfig:
    """从配置文件加载配置

    Returns:
        ServerConfig: 服务器配置对象

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误
    """
    config_file = Path("config.yaml")
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return ServerConfig(**config_data)
    except yaml.YAMLError as e:
        raise ValueError(f"配置文件格式错误: {e}")
    except Exception as e:
        raise ValueError(f"加载配置失败: {e}")


def load_config_from_env() -> Optional[ServerConfig]:
    """从环境变量加载配置
    
    Returns:
        ServerConfig: 服务器配置对象，如果必需的环境变量不存在则返回 None
    """
    s3_config = S3Config.from_env()
    if s3_config is None:
        return None
        
    mcp_server_config = MCPServerConfig.from_env()
    log_level = os.getenv('MCP_LOG_LEVEL', 'INFO')
    
    return ServerConfig(
        s3=s3_config,
        mcp_server=mcp_server_config,
        log_level=log_level
    )


def load_config() -> ServerConfig:
    """加载配置，优先使用环境变量，然后回退到配置文件

    Returns:
        ServerConfig: 服务器配置对象

    Raises:
        FileNotFoundError: 配置文件不存在且环境变量不完整
        ValueError: 配置文件格式错误
    """
    # 首先尝试从环境变量加载
    env_config = load_config_from_env()
    if env_config is not None:
        return env_config
    
    # 如果环境变量不完整，则从配置文件加载
    return load_config_from_file()


_config = None


def get_config():
    """获取配置"""
    global _config
    if _config is None:
        _config = load_config()
    return _config

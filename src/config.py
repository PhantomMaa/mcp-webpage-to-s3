"""配置管理模块"""

from typing import Optional
from pydantic import BaseModel, Field
import os
import yaml
from pathlib import Path


class LibcloudConfig(BaseModel):
    """云存储配置"""
    remote_type: str = Field(description="远程存储类型，如 s3, oss 等")
    access_key_id: str = Field(description="访问密钥 ID")
    secret_access_key: str = Field(description="访问密钥")
    endpoint: Optional[str] = Field(default=None, description="存储服务端点")
    region: Optional[str] = Field(default=None, description="存储区域")
    bucket: str = Field(description="存储桶名称")
    base_path: str = Field(default="", description="基础路径前缀")
    remote_name: str = Field(default="myremote", description="远程名称")


class MCPServerConfig(BaseModel):
    """MCP 服务器配置"""
    transport: str = Field(default="stdio", description="传输协议：stdio, sse, streamable-http")
    port: int = Field(default=8000, description="MCP 服务器端口")


class ServerConfig(BaseModel):
    """MCP 服务器配置"""
    libcloud: LibcloudConfig
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    log_level: str = Field(default="INFO", description="日志级别")


def load_config(config_path: Optional[str] = None) -> ServerConfig:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为 None 则使用默认路径
        
    Returns:
        ServerConfig: 服务器配置对象
        
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误
    """
    if config_path is None:
        # 默认配置文件路径
        config_path = os.getenv("MCP_LIBCLOUD_CONFIG", "config.yaml")
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return ServerConfig(**config_data)
    except yaml.YAMLError as e:
        raise ValueError(f"配置文件格式错误: {e}")
    except Exception as e:
        raise ValueError(f"加载配置失败: {e}")

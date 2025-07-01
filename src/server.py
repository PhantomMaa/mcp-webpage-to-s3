"""MCP Libcloud Server 主要实现"""

import asyncio
import signal
import sys
from typing import Any, Dict

from fastmcp import FastMCP
from loguru import logger

from src.config import ServerConfig
from src.s3_wrapper import S3Wrapper, StorageError

from nanoid import generate
from src.logger import setup_logging
from src.config import get_config


class MCPLibcloudServer:
    """MCP Libcloud 服务器"""

    def __init__(self, config: ServerConfig):
        """初始化服务器

        Args:
            config: 服务器配置
        """
        self.config = config

        # 初始化存储包装器
        try:
            self.storage = S3Wrapper(config.s3)
            logger.info("存储包装器初始化成功")
        except Exception as e:
            logger.error(f"存储包装器初始化失败: {e}")
            raise

        # 配置日志
        logger.remove()
        logger.add(
            sys.stderr,
            level=config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

        # 初始化 FastMCP
        self.mcp = FastMCP("MCP Libcloud Server")
        self._register_tools()

    def _register_tools(self) -> None:
        """注册 MCP 工具"""

        @self.mcp.tool()
        async def deploy_html(html_content: str) -> Dict[str, Any]:
            """部署 HTML 文件到远程存储

            Args:
                html_content: HTML 文件内容

            Returns:
                Dict: 包含部署结果和文件 URL 的字典
            """
            try:
                logger.info(f"开始部署 HTML 文件")

                # 使用 nanoid 生成随机文件名，确保唯一性
                filename = generate(size=16)

                # 使用存储包装器的专用方法上传 HTML 内容
                file_url = self.storage.upload_html_content(
                    html_content=html_content,
                    filename=filename,
                )

                logger.info(f"HTML 文件部署成功: {file_url}")

                return {
                    "success": True,
                    "message": "HTML 文件部署成功",
                    "url": file_url,
                }

            except StorageError as e:
                error_msg = f"HTML 部署失败: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"HTML 部署异常: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}


def run_server():
    """运行 MCP Libcloud Server"""

    setup_logging()

    # 设置信号处理器来优雅地处理关闭
    shutdown_event = asyncio.Event()

    # 设置信号处理函数
    def signal_handler(sig, frame):
        logger.info("收到终止信号，正在优雅关闭服务...")
        sys.exit(0)

    # 注册 SIGINT 信号处理函数（Ctrl+C）
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 加载配置并创建服务器
        config = get_config()
        server = MCPLibcloudServer(config)

        # 根据传输协议选择合适的启动方式
        transport = config.mcp_server.transport

        if transport == "stdio":
            asyncio.run(server.mcp.run_async())
        else:
            logger.info(f"启动 {transport} 传输模式")
            # 使用更优雅的方式启动服务器
            server.mcp.run(
                transport=transport,
                host="0.0.0.0",
                port=server.config.mcp_server.port,
            )
        logger.info("服务已关闭")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

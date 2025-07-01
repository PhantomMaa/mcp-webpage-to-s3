import asyncio
import signal
import sys
from typing import Any, Dict

from fastmcp import FastMCP
from pydantic import Field
from loguru import logger

from src.deploy import upload_html_content

from nanoid import generate
from src.logger import setup_logging
from src.config import get_config

# 创建 MCP 服务器
mcp = FastMCP("mcp-web-deploy", stateless_http=True, json_response=True)


@mcp.tool(name="deploy_html_to_s3", description="部署网页到 S3 存储")
def deploy_html_to_s3(html_content: str = Field(description="网页内容")) -> Dict[str, Any]:
    try:
        logger.info("开始部署 HTML 内容")

        # 使用 nanoid 生成随机文件名，确保唯一性
        filename = generate(alphabet="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", size=16)

        # 使用存储包装器的专用方法上传 HTML 内容
        file_url = upload_html_content(html_content=html_content, filename=filename)

        logger.info(f"HTML 文件部署成功: {file_url}")

        return {
            "success": True,
            "message": "HTML 文件部署成功",
            "url": file_url
        }

    except Exception as e:
        error_msg = f"HTML 部署异常: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def run_server():
    """运行 MCP Libcloud Server"""

    setup_logging()

    # 设置信号处理函数
    def signal_handler(sig, frame):
        logger.info("收到终止信号，正在优雅关闭服务...")
        sys.exit(0)

    # 注册 SIGINT 信号处理函数（Ctrl+C）
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("mcp web deploy 服务启动...")

    try:
        # 加载配置并创建服务器
        config = get_config()

        # 根据传输协议选择合适的启动方式
        transport = config.mcp_server.transport

        logger.info(f"启动 {transport} 传输模式")
        if transport == "stdio":
            asyncio.run(mcp.run_async())
            logger.info("服务启动成功")
        else:
            # 使用更优雅的方式启动服务器
            mcp.run(transport=transport, host="0.0.0.0", port=config.mcp_server.port)

    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务发生异常: {e}")

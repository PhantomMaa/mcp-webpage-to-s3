"""MCP Libcloud Server 主要实现"""

import asyncio
from typing import Any, Dict

from fastmcp import FastMCP
from loguru import logger
import sys

from .config import load_config, ServerConfig, create_sample_config
from .libcloud_wrapper import LibcloudStorageWrapper, StorageError


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
            self.storage = LibcloudStorageWrapper(config.libcloud)
            logger.info("存储包装器初始化成功")
        except Exception as e:
            logger.error(f"存储包装器初始化失败: {e}")
            raise
        
        # 配置日志
        logger.remove()
        logger.add(
            sys.stderr,
            level=config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # 初始化 FastMCP
        self.mcp = FastMCP("MCP Libcloud Server")
        self._register_tools()
    
    def _register_tools(self) -> None:
        """注册 MCP 工具"""
        
        @self.mcp.tool()
        async def deploy_html(
            html_content: str,
            filename: str = "index.html",
            remote_path: str = ""
        ) -> Dict[str, Any]:
            """部署 HTML 文件到远程存储
            
            Args:
                html_content: HTML 文件内容
                filename: 文件名，默认为 index.html
                remote_path: 远程路径（相对于配置的 base_path），默认为根目录
                
            Returns:
                Dict: 包含部署结果和文件 URL 的字典
            """
            try:
                logger.info(f"开始部署 HTML 文件: {filename}")
                
                # 验证文件名
                if not filename.endswith('.html'):
                    filename += '.html'
                
                # 使用存储包装器的专用方法上传 HTML 内容
                file_url = self.storage.upload_html_content(
                    html_content=html_content,
                    filename=filename,
                    remote_path=remote_path
                )
                
                logger.info(f"HTML 文件部署成功: {file_url}")
                
                return {
                    "success": True,
                    "message": "HTML 文件部署成功",
                    "filename": filename,
                    "remote_path": remote_path,
                    "url": file_url,
                    "size_bytes": len(html_content.encode('utf-8'))
                }
                        
            except StorageError as e:
                error_msg = f"HTML 部署失败: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "filename": filename
                }
            except Exception as e:
                error_msg = f"HTML 部署异常: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "filename": filename
                }
        
        @self.mcp.tool()
        async def check_status() -> Dict[str, Any]:
            """检查服务器状态和存储连接
            
            Returns:
                Dict: 服务器状态信息
            """
            try:
                logger.info("检查服务器状态")
                
                # 检查存储连接
                connection_ok = self.storage.check_connection()
                
                return {
                    "success": True,
                    "server_status": "running",
                    "storage_connection": "ok" if connection_ok else "failed",
                    "remote_name": self.config.libcloud.remote_name,
                    "bucket": self.config.libcloud.bucket,
                    "base_path": self.config.libcloud.base_path
                }
                
            except Exception as e:
                error_msg = f"状态检查异常: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
    
    async def run(self) -> None:
        """运行 MCP 服务器"""
        logger.info("启动 MCP Libcloud Server")
        
        # 检查存储连接
        if not self.storage.check_connection():
            logger.warning("存储连接检查失败，但服务器将继续运行")
        
        # 运行 MCP 服务器 - 使用异步方法避免嵌套事件循环
        await self.mcp.run_async()


def run_server():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Libcloud Server")
    parser.add_argument(
        "--config", 
        type=str, 
        help="配置文件路径"
    )
    parser.add_argument(
        "--create-sample-config",
        action="store_true",
        help="创建示例配置文件"
    )
    
    args = parser.parse_args()
    
    if args.create_sample_config:
        create_sample_config()
        print("示例配置文件已创建: config.yaml.sample")
        return
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 创建服务器
        server = MCPLibcloudServer(config)
        
        # 清理现有的事件循环
        try:
            # 关闭现有的事件循环（如果有的话）
            try:
                current_loop = asyncio.get_event_loop()
                if current_loop.is_running():
                    current_loop.stop()
                current_loop.close()
            except RuntimeError:
                pass  # 没有现有的循环
            
            # 设置新的事件循环策略
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            
            # 创建并设置新的事件循环
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            # 运行服务器
            new_loop.run_until_complete(server.run())
            
        except KeyboardInterrupt:
            print("\n收到中断信号，正在关闭服务器...")
        finally:
            # 清理资源
            try:
                loop = asyncio.get_event_loop()
                loop.close()
            except:
                pass
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("请先创建配置文件，或使用 --create-sample-config 创建示例配置")
        sys.exit(1)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)


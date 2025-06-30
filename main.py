#!/usr/bin/env python3
"""MCP Libcloud Server 入口点"""

from src.server import run_server

if __name__ == "__main__":
    # 直接调用 run_server，让它根据传输协议选择合适的启动方式
    run_server()

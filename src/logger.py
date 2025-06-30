import sys
from loguru import logger


def setup_logging():
    """配置日志系统"""
    # 清除默认处理器
    logger.remove()

    # 定义统一的日志格式
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # 添加控制台日志
    logger.add(sys.stdout, colorize=True, format=log_format, level="DEBUG")

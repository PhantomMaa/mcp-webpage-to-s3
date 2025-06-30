"""基于 Apache Libcloud 的云存储包装器"""

import tempfile
import os
from loguru import logger

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from libcloud.common.exceptions import BaseHTTPError

from src.config import S3Config


class StorageError(Exception):
    """存储操作异常"""

    pass


class LibcloudStorageWrapper:
    """基于 Apache Libcloud 的云存储包装器"""

    def __init__(self, config: S3Config):
        """初始化存储包装器

        Args:
            config: 存储配置
        """
        self.config = config
        self.driver = self._create_driver()
        logger.info("初始化 libcloud 存储")

    def _create_driver(self):
        """创建存储驱动"""
        try:
            driver_cls = get_driver(Provider.S3)
            driver_kwargs = {"key": self.config.access_key_id, "secret": self.config.secret_access_key}

            driver_kwargs["region"] = self.config.region
            driver_kwargs["host"] = self.config.endpoint.replace("https://", "").replace("http://", "")
            if not self.config.endpoint.startswith("https://"):
                driver_kwargs["secure"] = False

            return driver_cls(**driver_kwargs)

        except Exception as e:
            raise StorageError(f"创建存储驱动失败: {str(e)}")

    def _upload_file(self, local_path: str, file_name: str) -> str:
        """上传文件到远程存储

        Args:
            local_path: 本地文件路径
            file_name: 文件名

        Returns:
            str: 上传后的文件 URL

        Raises:
            StorageError: 上传失败
        """
        if not os.path.exists(local_path):
            raise StorageError(f"本地文件不存在: {local_path}")

        try:
            # 获取或创建容器
            container = self.driver.get_container(self.config.bucket)

            # 上传文件，设置正确的 Content-Type
            with open(local_path, "rb") as file_obj:
                self.driver.upload_object_via_stream(
                    iterator=file_obj, container=container, object_name=file_name, extra={"content_type": "text/html"}
                )

            # 生成文件 URL
            return f"https://{self.config.bucket}.s3.{self.config.region}.amazonaws.com/{file_name}"

        except BaseHTTPError as e:
            error_msg = f"HTTP 错误: {e.code} - {e.message}"
            logger.error(error_msg)
            raise StorageError(error_msg)
        except Exception as e:
            error_msg = f"文件上传失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)

    def upload_html_content(self, html_content: str, filename: str) -> str:
        """上传 HTML 内容到远程存储

        Args:
            html_content: HTML 内容
            filename: 文件名

        Returns:
            str: 上传后的文件 URL

        Raises:
            StorageError: 上传失败
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as temp_file:
                temp_file.write(html_content)
                temp_path = temp_file.name

            try:
                # 上传文件
                file_url = self._upload_file(temp_path, filename)
                logger.info(f"HTML 内容上传成功: {file_url}")

                return file_url

            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            error_msg = f"HTML 内容上传失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)

"""基于 Boto3 的 S3 存储包装器"""

import tempfile
import os
from loguru import logger
import hashlib
import base64

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from src.config import S3Config


class StorageError(Exception):
    """存储操作异常"""

    pass


class S3Wrapper:
    """基于 Boto3 的 S3 存储包装器
    
    注意：为了保持向后兼容性，类名保持不变
    """

    def __init__(self, config: S3Config):
        """初始化存储包装器

        Args:
            config: S3 存储配置
        """
        self.config = config
        self.s3_client = self._create_s3_client()
        logger.info("初始化 boto3 S3 客户端")

    def _create_s3_client(self):
        """创建 S3 客户端"""
        try:
            # 构建 boto3 客户端配置
            client_config = {
                "aws_access_key_id": self.config.access_key_id,
                "aws_secret_access_key": self.config.secret_access_key,
                "region_name": self.config.region,
            }
            
            # 如果有自定义 endpoint，添加到配置中
            if self.config.endpoint:
                client_config["endpoint_url"] = self.config.endpoint

            return boto3.client("s3", **client_config)

        except Exception as e:
            raise StorageError(f"创建 S3 客户端失败: {str(e)}")

    def calc_sha256(self, content: bytes):
        hash = hashlib.sha256()
        hash.update(content)
        return hash.hexdigest(), base64.b64encode(hash.digest()).decode()

    def _upload_file(self, local_path: str, file_name: str) -> str:
        """上传文件到 S3 存储

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
            # 上传文件到 S3，设置正确的 Content-Type
            with open(local_path, "rb") as file_obj:
                file_content = file_obj.read()
                _, sha256_b64 = self.calc_sha256(file_content)
                file_obj.seek(0)
                self.s3_client.put_object(
                    Bucket=self.config.bucket,
                    Key=file_name,
                    Body=file_obj,
                    ContentType="text/html",  # 设置 Content-Type 为 HTML
                    ChecksumSHA256=sha256_b64,  # 传递 base64 格式的 SHA256
                )

            # 生成文件 URL
            return f"{self.config.base_url.rstrip('/')}/{file_name}"

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = f"S3 客户端错误: {error_code} - {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise StorageError(error_msg)
        except BotoCoreError as e:
            error_msg = f"Boto3 核心错误: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)
        except Exception as e:
            error_msg = f"文件上传失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)

    def upload_html_content(self, html_content: str, filename: str) -> str:
        """上传 HTML 内容到 S3 存储

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

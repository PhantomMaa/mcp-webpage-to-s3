import os
import boto3
from botocore.exceptions import ClientError
from loguru import logger
from src.config import get_config


class StorageError(Exception):
    """存储操作相关的异常"""
    pass


class S3Client:

    def __init__(self):
        config = get_config()
        if not config.s3:
            logger.error("S3 配置未找到，无法初始化 S3 客户端")
            self.s3_client = None
            self.s3_config = None
            return

        self.s3_config = config.s3
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.s3_config.access_key,
            aws_secret_access_key=self.s3_config.secret_key,
            endpoint_url=self.s3_config.endpoint,
            region_name=self.s3_config.region,
        )

    def upload_file(self, local_file_path, s3_file_name=None, ExtraArgs=None):
        if not self.s3_client or not self.s3_config:
            error_msg = "S3 客户端未初始化，无法上传文件"
            logger.error(error_msg)
            raise StorageError(error_msg)

        if s3_file_name is None:
            s3_file_name = os.path.basename(local_file_path)
        try:
            self.s3_client.upload_file(
                local_file_path,
                self.s3_config.bucket,
                s3_file_name,
                ExtraArgs=ExtraArgs,
            )
            file_url = f"{self.s3_config.base_url}/{s3_file_name}"
            logger.info(f"文件已成功上传到 S3: {file_url}")
            return file_url
        except ClientError as e:
            error_msg = f"上传文件到 S3 时出错: {e}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e

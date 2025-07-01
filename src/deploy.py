from src.s3 import S3Client
import tempfile
import os
from loguru import logger

s3_client = S3Client()


def upload_html_content(html_content: str, filename: str) -> str:
    """上传 HTML 内容到 S3 存储"""
    temp_path = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_path = temp_file.name

        # 上传文件
        file_url = s3_client.upload_file(
            temp_path,
            filename,
            ExtraArgs={
                "ContentType": "text/html",
                "ContentDisposition": "inline",
                "CacheControl": "max-age=31536000",
            },
        )
        logger.info(f"HTML 内容上传成功: {file_url}")

        return file_url

    except Exception as e:
        error_msg = f"HTML 内容上传失败: {str(e)}"
        logger.error(error_msg)
        raise
    finally:
        # 清理临时文件
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

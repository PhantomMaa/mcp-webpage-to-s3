"""Apache Libcloud 实现示例 - 用于对比分析"""

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerDoesNotExistError
import tempfile
import os
from typing import Dict, Any


class LibcloudStorageWrapper:
    """基于 Apache Libcloud 的存储包装器"""
    
    def __init__(self, provider: str, access_key: str, secret_key: str, 
                 region: str = None, endpoint: str = None):
        """初始化存储驱动
        
        Args:
            provider: 存储提供商 (s3, oss, gcs 等)
            access_key: 访问密钥
            secret_key: 密钥
            region: 区域
            endpoint: 自定义端点
        """
        # 获取驱动类
        if provider.lower() == 's3':
            driver_cls = get_driver(Provider.S3)
        elif provider.lower() == 'oss':
            driver_cls = get_driver(Provider.ALIYUN_OSS)
        elif provider.lower() == 'gcs':
            driver_cls = get_driver(Provider.GOOGLE_STORAGE)
        else:
            raise ValueError(f"不支持的存储提供商: {provider}")
        
        # 初始化驱动
        driver_kwargs = {
            'key': access_key,
            'secret': secret_key
        }
        
        if region:
            driver_kwargs['region'] = region
        if endpoint:
            driver_kwargs['host'] = endpoint.replace('https://', '').replace('http://', '')
            
        self.driver = driver_cls(**driver_kwargs)
        self.provider = provider
    
    def upload_file(self, local_path: str, bucket: str, remote_path: str, 
                   base_path: str = "") -> Dict[str, Any]:
        """上传文件
        
        Args:
            local_path: 本地文件路径
            bucket: 存储桶名称
            remote_path: 远程文件路径
            base_path: 基础路径前缀
            
        Returns:
            Dict: 上传结果，包含 URL 和元信息
        """
        try:
            # 获取或创建容器
            try:
                container = self.driver.get_container(bucket)
            except ContainerDoesNotExistError:
                container = self.driver.create_container(bucket)
            
            # 构建完整的远程路径
            if base_path:
                full_remote_path = f"{base_path.strip('/')}/{remote_path.strip('/')}"
            else:
                full_remote_path = remote_path.strip('/')
            
            # 上传文件
            with open(local_path, 'rb') as file_obj:
                obj = self.driver.upload_object_via_stream(
                    iterator=file_obj,
                    container=container,
                    object_name=full_remote_path
                )
            
            # 生成访问 URL
            file_url = self._generate_url(bucket, full_remote_path)
            
            return {
                "success": True,
                "url": file_url,
                "size": obj.size,
                "remote_path": full_remote_path,
                "etag": getattr(obj, 'hash', None)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_html_content(self, html_content: str, bucket: str, 
                           filename: str = "index.html", remote_path: str = "",
                           base_path: str = "") -> Dict[str, Any]:
        """上传 HTML 内容
        
        Args:
            html_content: HTML 内容
            bucket: 存储桶名称
            filename: 文件名
            remote_path: 远程路径
            base_path: 基础路径前缀
            
        Returns:
            Dict: 上传结果
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', 
                                           delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                temp_path = temp_file.name
            
            try:
                # 构建远程文件路径
                if remote_path:
                    full_remote_path = f"{remote_path.strip('/')}/{filename}"
                else:
                    full_remote_path = filename
                
                # 上传文件
                result = self.upload_file(temp_path, bucket, full_remote_path, base_path)
                
                if result["success"]:
                    result["filename"] = filename
                    result["size_bytes"] = len(html_content.encode('utf-8'))
                
                return result
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _generate_url(self, bucket: str, remote_path: str) -> str:
        """生成文件访问 URL"""
        if self.provider.lower() == 's3':
            return f"https://{bucket}.s3.amazonaws.com/{remote_path}"
        elif self.provider.lower() == 'oss':
            return f"https://{bucket}.oss.aliyuncs.com/{remote_path}"
        else:
            # 通用格式
            return f"https://{bucket}.{self.provider}.com/{remote_path}"
    
    def check_connection(self, bucket: str) -> bool:
        """检查连接状态"""
        try:
            self.driver.get_container(bucket)
            return True
        except Exception:
            return False


# 使用示例
if __name__ == "__main__":
    # 初始化存储包装器
    storage = LibcloudStorageWrapper(
        provider="s3",
        access_key="your_access_key",
        secret_key="your_secret_key",
        region="us-east-1"
    )
    
    # 上传 HTML 内容
    html_result = storage.upload_html_content(
        html_content="<html><body><h1>Hello World</h1></body></html>",
        bucket="my-bucket",
        filename="index.html",
        base_path="uploads"
    )
    print("HTML 上传结果:", html_result)
    
    # 上传文件
    file_result = storage.upload_file(
        local_path="/path/to/file.txt",
        bucket="my-bucket", 
        remote_path="documents/file.txt",
        base_path="uploads"
    )
    print("文件上传结果:", file_result)

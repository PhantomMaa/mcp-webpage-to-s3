"""基于 Apache Libcloud 的云存储包装器"""

import tempfile
import os
from loguru import logger

from libcloud.storage.types import Provider, ContainerDoesNotExistError
from libcloud.storage.providers import get_driver
from libcloud.common.exceptions import BaseHTTPError

from .config import LibcloudConfig


class StorageError(Exception):
    """存储操作异常"""
    pass


class LibcloudStorageWrapper:
    """基于 Apache Libcloud 的云存储包装器"""
    
    def __init__(self, config: LibcloudConfig):
        """初始化存储包装器
        
        Args:
            config: 存储配置
        """
        self.config = config
        self.driver = self._create_driver()
        logger.info(f"初始化 {config.remote_type} 存储")
    
    def _create_driver(self):
        """创建存储驱动"""
        try:
            # 根据存储类型选择驱动
            if self.config.remote_type.lower() == 's3':
                driver_cls = get_driver(Provider.S3)
                driver_kwargs = {
                    'key': self.config.access_key_id,
                    'secret': self.config.secret_access_key
                }
                
                # 添加区域配置
                if self.config.region:
                    driver_kwargs['region'] = self.config.region
                
                # 添加自定义端点配置
                if self.config.endpoint:
                    # 解析端点 URL
                    endpoint = self.config.endpoint.replace('https://', '').replace('http://', '')
                    driver_kwargs['host'] = endpoint
                    
                    # 如果是自定义端点，可能需要设置安全连接
                    if not self.config.endpoint.startswith('https://'):
                        driver_kwargs['secure'] = False
                        
            elif self.config.remote_type.lower() == 'oss':
                driver_cls = get_driver(Provider.ALIYUN_OSS)
                driver_kwargs = {
                    'key': self.config.access_key_id,
                    'secret': self.config.secret_access_key
                }
                
                # OSS 需要指定区域
                if self.config.region:
                    driver_kwargs['region'] = self.config.region
                elif self.config.endpoint:
                    # 从端点提取区域信息
                    if 'oss-' in self.config.endpoint:
                        region = self.config.endpoint.split('oss-')[1].split('.')[0]
                        driver_kwargs['region'] = region
                        # 同时更新配置中的区域信息
                        self.config.region = region
                else:
                    # 默认区域
                    driver_kwargs['region'] = 'cn-hangzhou'
                    self.config.region = 'cn-hangzhou'
                        
            else:
                raise StorageError(f"不支持的存储类型: {self.config.remote_type}")
            
            return driver_cls(**driver_kwargs)
            
        except Exception as e:
            raise StorageError(f"创建存储驱动失败: {str(e)}")
    
    def _upload_file(self, local_path: str, remote_path: str) -> str:
        """上传文件到远程存储
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径（相对于 bucket 根目录）
            
        Returns:
            str: 上传后的文件 URL
            
        Raises:
            StorageError: 上传失败
        """
        if not os.path.exists(local_path):
            raise StorageError(f"本地文件不存在: {local_path}")
        
        try:
            # 获取或创建容器
            container = self._get_or_create_container()
            
            # 构建完整的远程路径
            full_remote_path = self._build_remote_path(remote_path)
            
            # 上传文件
            with open(local_path, 'rb') as file_obj:
                obj = self.driver.upload_object_via_stream(
                    iterator=file_obj,
                    container=container,
                    object_name=full_remote_path
                )
            
            # 生成文件 URL
            file_url = self._generate_file_url(full_remote_path)
            logger.info(f"文件上传成功: {local_path} -> {file_url}")
            
            return file_url
            
        except BaseHTTPError as e:
            error_msg = f"HTTP 错误: {e.code} - {e.message}"
            logger.error(error_msg)
            raise StorageError(error_msg)
        except Exception as e:
            error_msg = f"文件上传失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)
    
    def upload_html_content(self, html_content: str, filename: str = "index.html", 
                           remote_path: str = "") -> str:
        """上传 HTML 内容到远程存储
        
        Args:
            html_content: HTML 内容
            filename: 文件名
            remote_path: 远程路径
            
        Returns:
            str: 上传后的文件 URL
            
        Raises:
            StorageError: 上传失败
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False, encoding='utf-8'
            ) as temp_file:
                temp_file.write(html_content)
                temp_path = temp_file.name
            
            try:
                # 构建远程文件路径
                if remote_path:
                    full_remote_path = f"{remote_path.strip('/')}/{filename}"
                else:
                    full_remote_path = filename
                
                # 上传文件
                file_url = self._upload_file(temp_path, full_remote_path)
                logger.info(f"HTML 内容上传成功: {filename} -> {file_url}")
                
                return file_url
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            error_msg = f"HTML 内容上传失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg)
    
    def _get_or_create_container(self):
        """获取或创建存储容器"""
        try:
            return self.driver.get_container(self.config.bucket)
        except ContainerDoesNotExistError:
            logger.info(f"容器不存在，创建新容器: {self.config.bucket}")
            return self.driver.create_container(self.config.bucket)
    
    def _build_remote_path(self, remote_path: str) -> str:
        """构建完整的远程路径"""
        path_parts = []
        
        if self.config.base_path:
            path_parts.append(self.config.base_path.strip('/'))
        
        if remote_path:
            path_parts.append(remote_path.strip('/'))
        
        return '/'.join(path_parts) if path_parts else remote_path.strip('/')
    
    def _generate_file_url(self, remote_path: str) -> str:
        """生成文件访问 URL
        
        Args:
            remote_path: 远程文件路径
            
        Returns:
            str: 文件访问 URL
        """
        if self.config.remote_type.lower() == 's3':
            if self.config.endpoint and not self.config.endpoint.endswith('amazonaws.com'):
                # 自定义端点（非AWS）
                base_url = self.config.endpoint.rstrip('/')
                if not base_url.startswith(('http://', 'https://')):
                    base_url = f"https://{base_url}"
                return f"{base_url}/{self.config.bucket}/{remote_path}"
            else:
                # 标准 S3 URL - 使用虚拟主机样式
                region = self.config.region or 'us-east-1'
                return f"https://{self.config.bucket}.s3.{region}.amazonaws.com/{remote_path}"
                    
        elif self.config.remote_type.lower() == 'oss':
            if self.config.endpoint:
                base_url = self.config.endpoint.rstrip('/')
                if not base_url.startswith(('http://', 'https://')):
                    base_url = f"https://{base_url}"
                return f"{base_url.replace('oss-', f'{self.config.bucket}.oss-')}/{remote_path}"
            else:
                # 标准 OSS URL
                region = self.config.region or 'cn-hangzhou'
                return f"https://{self.config.bucket}.oss-{region}.aliyuncs.com/{remote_path}"
        
        # 通用格式
        return f"https://{self.config.bucket}.{self.config.remote_type}.com/{remote_path}"
    
    def check_connection(self) -> bool:
        """检查与远程存储的连接
        
        Returns:
            bool: 连接是否正常
        """
        try:
            # 尝试列出容器来检查连接
            self.driver.list_containers()
            logger.info("存储连接检查成功")
            return True
            
        except Exception as e:
            logger.error(f"存储连接检查失败: {str(e)}")
            return False


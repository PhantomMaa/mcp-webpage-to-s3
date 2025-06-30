"""测试基于 Apache Libcloud 的存储包装器"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mcp_libcloud.libcloud_wrapper import LibcloudStorageWrapper, StorageError
from mcp_libcloud.config import LibcloudConfig

@pytest.fixture
def sample_config():
    """创建测试用的配置"""
    return LibcloudConfig(
        remote_name="test-remote",
        remote_type="s3",
        access_key_id="test-access-key",
        secret_access_key="test-secret-key",
        bucket="test-bucket",
        region="us-east-1",
        endpoint="https://s3.amazonaws.com",
        base_path="uploads"
    )


@pytest.fixture
def mock_driver():
    """创建模拟的存储驱动"""
    driver = Mock()
    container = Mock()
    container.name = "test-bucket"
    driver.get_container.return_value = container
    driver.create_container.return_value = container
    driver.list_containers.return_value = [container]
    return driver


@pytest.fixture
def storage_wrapper(sample_config, mock_driver):
    """创建存储包装器实例"""
    with patch('mcp_libcloud.libcloud_wrapper.get_driver') as mock_get_driver:
        mock_driver_cls = Mock()
        mock_driver_cls.return_value = mock_driver
        mock_get_driver.return_value = mock_driver_cls
        
        wrapper = LibcloudStorageWrapper(sample_config)
        wrapper.driver = mock_driver
        return wrapper


class TestLibcloudStorageWrapper:
    """测试 LibcloudStorageWrapper 类"""
    
    @patch('mcp_libcloud.libcloud_wrapper.get_driver')
    def test_init_s3(self, mock_get_driver, sample_config):
        """测试 S3 存储初始化"""
        mock_driver_cls = Mock()
        mock_driver = Mock()
        mock_driver_cls.return_value = mock_driver
        mock_get_driver.return_value = mock_driver_cls
        
        wrapper = LibcloudStorageWrapper(sample_config)
        
        assert wrapper.config == sample_config
        mock_get_driver.assert_called_once()
        mock_driver_cls.assert_called_once_with(
            key='test-access-key',
            secret='test-secret-key',
            region='us-east-1',
            host='s3.amazonaws.com'
        )
    
    @patch('mcp_libcloud.libcloud_wrapper.get_driver')
    def test_init_oss(self, mock_get_driver, sample_config):
        """测试 OSS 存储初始化"""
        sample_config.remote_type = "oss"
        sample_config.endpoint = "https://oss-cn-hangzhou.aliyuncs.com"
        sample_config.region = None  # 清空区域，让代码从端点提取
        
        mock_driver_cls = Mock()
        mock_driver = Mock()
        mock_driver_cls.return_value = mock_driver
        mock_get_driver.return_value = mock_driver_cls
        
        wrapper = LibcloudStorageWrapper(sample_config)
        
        mock_driver_cls.assert_called_once_with(
            key='test-access-key',
            secret='test-secret-key',
            region='cn-hangzhou'
        )
    
    def test_init_unsupported_type(self, sample_config):
        """测试不支持的存储类型"""
        sample_config.remote_type = "unsupported"
        
        with pytest.raises(StorageError, match="不支持的存储类型"):
            LibcloudStorageWrapper(sample_config)
    
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_upload_file_success(self, mock_exists, mock_open, storage_wrapper):
        """测试成功上传文件"""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_obj = Mock()
        mock_obj.size = 1024
        storage_wrapper.driver.upload_object_via_stream.return_value = mock_obj
        
        file_url = storage_wrapper._upload_file("/path/to/file.txt", "documents/file.txt")
        
        expected_url = "https://test-bucket.s3.us-east-1.amazonaws.com/uploads/documents/file.txt"
        assert file_url == expected_url
        storage_wrapper.driver.upload_object_via_stream.assert_called_once()
    
    def test_upload_file_not_exists(self, storage_wrapper):
        """测试上传不存在的文件"""
        with pytest.raises(StorageError, match="本地文件不存在"):
            storage_wrapper._upload_file("/nonexistent/file.txt", "test.txt")
    
    @patch('os.path.exists')
    def test_upload_file_http_error(self, mock_exists, storage_wrapper):
        """测试上传文件 HTTP 错误"""
        from libcloud.common.exceptions import BaseHTTPError
        
        mock_exists.return_value = True
        storage_wrapper.driver.get_container.side_effect = BaseHTTPError(
            code=403, message="Access Denied"
        )
        
        with pytest.raises(StorageError, match="HTTP 错误: 403 - Access Denied"):
            storage_wrapper._upload_file("/path/to/file.txt", "test.txt")
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.path.exists')
    @patch('os.unlink')
    def test_upload_html_content_success(self, mock_unlink, mock_exists, mock_temp, storage_wrapper):
        """测试成功上传 HTML 内容"""
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.html"
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp.return_value = mock_temp_file
        
        mock_exists.return_value = True
        
        # 模拟 upload_file 方法
        with patch.object(storage_wrapper, 'upload_file') as mock_upload:
            mock_upload.return_value = "https://example.com/test.html"
            
            result = storage_wrapper.upload_html_content(
                "<html><body>Test</body></html>",
                "test.html",
                "pages"
            )
            
            assert result == "https://example.com/test.html"
            mock_upload.assert_called_once()
            mock_unlink.assert_called_once()
    
    def test_build_remote_path(self, storage_wrapper):
        """测试构建远程路径"""
        # 测试带基础路径
        path = storage_wrapper._build_remote_path("documents/file.txt")
        assert path == "uploads/documents/file.txt"
        
        # 测试无基础路径
        storage_wrapper.config.base_path = None
        path = storage_wrapper._build_remote_path("file.txt")
        assert path == "file.txt"
    
    def test_generate_file_url_s3(self, storage_wrapper):
        """测试生成 S3 文件 URL"""
        url = storage_wrapper._generate_file_url("documents/test.txt")
        expected = "https://test-bucket.s3.us-east-1.amazonaws.com/documents/test.txt"
        assert url == expected
    
    def test_generate_file_url_s3_custom_endpoint(self, storage_wrapper):
        """测试生成自定义端点 S3 文件 URL"""
        storage_wrapper.config.endpoint = "https://minio.example.com"
        url = storage_wrapper._generate_file_url("documents/test.txt")
        expected = "https://minio.example.com/test-bucket/documents/test.txt"
        assert url == expected
    
    def test_generate_file_url_oss(self, sample_config, mock_driver):
        """测试生成 OSS 文件 URL"""
        # 创建 OSS 配置
        sample_config.remote_type = "oss"
        sample_config.region = "cn-hangzhou"
        sample_config.endpoint = None  # 清空 endpoint，使用标准 OSS URL
        
        # 创建 OSS 存储包装器
        oss_wrapper = LibcloudStorageWrapper.__new__(LibcloudStorageWrapper)
        oss_wrapper.config = sample_config
        oss_wrapper.driver = mock_driver
        
        url = oss_wrapper._generate_file_url("documents/test.txt")
        expected = "https://test-bucket.oss-cn-hangzhou.aliyuncs.com/documents/test.txt"
        assert url == expected
    
    def test_check_connection_success(self, storage_wrapper):
        """测试连接检查成功"""
        result = storage_wrapper.check_connection()
        assert result is True
        storage_wrapper.driver.list_containers.assert_called_once()
    
    def test_check_connection_failure(self, storage_wrapper):
        """测试连接检查失败"""
        storage_wrapper.driver.list_containers.side_effect = Exception("Connection failed")
        
        result = storage_wrapper.check_connection()
        assert result is False
    
    def test_get_or_create_container_exists(self, storage_wrapper):
        """测试获取已存在的容器"""
        container = storage_wrapper._get_or_create_container()
        assert container.name == "test-bucket"
        storage_wrapper.driver.get_container.assert_called_once_with("test-bucket")
    
    def test_get_or_create_container_create_new(self, storage_wrapper):
        """测试创建新容器"""
        from libcloud.storage.types import ContainerDoesNotExistError
        
        storage_wrapper.driver.get_container.side_effect = ContainerDoesNotExistError(
            value="Container not found", driver=storage_wrapper.driver, container_name="test-bucket"
        )
        
        container = storage_wrapper._get_or_create_container()
        assert container.name == "test-bucket"
        storage_wrapper.driver.create_container.assert_called_once_with("test-bucket")

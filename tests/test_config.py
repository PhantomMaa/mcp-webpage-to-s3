"""配置模块测试"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from mcp_libcloud.config import (
    LibcloudConfig,
    ServerConfig,
    load_config,
    create_sample_config
)


class TestLibcloudConfig:
    """LibcloudConfig 测试类"""
    
    def test_libcloud_config_creation(self):
        """测试 LibcloudConfig 创建"""
        config = LibcloudConfig(
            remote_name="test_remote",
            remote_type="s3",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket="test-bucket"
        )
        
        assert config.remote_name == "test_remote"
        assert config.remote_type == "s3"
        assert config.access_key_id == "test_key"
        assert config.secret_access_key == "test_secret"
        assert config.bucket == "test-bucket"
        assert config.base_path == ""
    
    def test_libcloud_config_with_optional_fields(self):
        """测试带可选字段的 LibcloudConfig"""
        config = LibcloudConfig(
            remote_name="test_remote",
            remote_type="s3",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket="test-bucket",
            endpoint="https://s3.example.com",
            region="us-west-2",
            base_path="uploads"
        )
        
        assert config.endpoint == "https://s3.example.com"
        assert config.region == "us-west-2"
        assert config.base_path == "uploads"


class TestServerConfig:
    """ServerConfig 测试类"""
    
    def test_server_config_creation(self):
        """测试 ServerConfig 创建"""
        libcloud_config = LibcloudConfig(
            remote_name="test_remote",
            remote_type="s3",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket="test-bucket"
        )
        
        config = ServerConfig(libcloud=libcloud_config)
        
        assert config.libcloud == libcloud_config
        assert config.log_level == "INFO"
    
    def test_server_config_with_custom_values(self):
        """测试自定义值的 ServerConfig"""
        libcloud_config = LibcloudConfig(
            remote_name="test_remote",
            remote_type="s3",
            access_key_id="test_key",
            secret_access_key="test_secret",
            bucket="test-bucket"
        )
        
        config = ServerConfig(
            libcloud=libcloud_config,
            log_level="DEBUG"
        )
        
        assert config.log_level == "DEBUG"


class TestConfigLoading:
    """配置加载测试类"""
    
    def test_load_config_success(self):
        """测试成功加载配置"""
        config_data = {
            "libcloud": {
                "remote_name": "myremote",
                "remote_type": "s3",
                "access_key_id": "test_key",
                "secret_access_key": "test_secret",
                "bucket": "test-bucket",
                "base_path": "uploads"
            },
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            
            assert config.libcloud.remote_name == "myremote"
            assert config.libcloud.remote_type == "s3"
            assert config.libcloud.access_key_id == "test_key"
            assert config.libcloud.secret_access_key == "test_secret"
            assert config.libcloud.bucket == "test-bucket"
            assert config.libcloud.base_path == "uploads"
            assert config.log_level == "DEBUG"
            
        finally:
            os.unlink(config_path)
    
    def test_load_config_file_not_found(self):
        """测试配置文件不存在"""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.yaml")
    
    def test_load_config_invalid_yaml(self):
        """测试无效的 YAML 格式"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="配置文件格式错误"):
                load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_create_sample_config(self):
        """测试创建示例配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_path = os.path.join(temp_dir, "test_sample.yaml")
            create_sample_config(sample_path)
            
            assert os.path.exists(sample_path)
            
            # 验证示例配置可以正常加载
            config = load_config(sample_path)
            assert config.libcloud.remote_name == "myremote"
            assert config.libcloud.remote_type == "s3"

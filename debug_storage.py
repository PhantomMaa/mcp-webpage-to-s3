#!/usr/bin/env python3
"""调试存储连接问题的脚本"""

import sys
import os
sys.path.insert(0, 'src')

from src.config import load_config
from src.libcloud_wrapper import LibcloudStorageWrapper
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

def test_storage_connection():
    """测试存储连接并提供调试信息"""
    try:
        # 加载配置
        config = load_config()
        print(f"配置加载成功:")
        print(f"  存储类型: {config.libcloud.remote_type}")
        print(f"  区域: {config.libcloud.region}")
        print(f"  端点: {config.libcloud.endpoint}")
        print(f"  存储桶: {config.libcloud.bucket}")
        print()
        
        # 检查 S3 驱动支持的区域
        if config.libcloud.remote_type.lower() == 's3':
            print("S3 驱动信息:")
            driver_cls = get_driver(Provider.S3)
            print(f"  驱动类: {driver_cls}")
            
            # 尝试创建驱动实例来测试参数
            print(f"  尝试使用区域 '{config.libcloud.region}' 创建驱动...")
            
            try:
                driver_kwargs = {
                    'key': config.libcloud.access_key_id,
                    'secret': config.libcloud.secret_access_key,
                    'region': config.libcloud.region
                }
                
                # 如果有自定义端点
                if config.libcloud.endpoint:
                    endpoint = config.libcloud.endpoint.replace('https://', '').replace('http://', '')
                    driver_kwargs['host'] = endpoint
                    print(f"  使用自定义端点: {endpoint}")
                
                driver = driver_cls(**driver_kwargs)
                print("  驱动创建成功")
                
                # 尝试连接测试
                print("  测试连接...")
                containers = driver.list_containers()
                print(f"  连接成功！找到 {len(containers)} 个容器")
                for container in containers:
                    print(f"    - {container.name}")
                    
            except Exception as e:
                print(f"  连接失败: {e}")
                print(f"  错误类型: {type(e).__name__}")
                
                # 提供修复建议
                print("\n修复建议:")
                if 'ap-east-1' in str(config.libcloud.region):
                    print("  1. ap-east-1 区域可能不被 Apache Libcloud 支持")
                    print("  2. 建议使用以下支持的区域之一:")
                    print("     - us-east-1 (美国东部)")
                    print("     - us-west-2 (美国西部)")
                    print("     - eu-west-1 (欧洲)")
                    print("     - ap-southeast-1 (亚太新加坡)")
                    print("  3. 同时需要更新对应的 endpoint")
                
                if 'Unexpected status code: 400' in str(e):
                    print("  HTTP 400 错误通常表示:")
                    print("     - 认证信息不正确")
                    print("     - 区域配置不支持")
                    print("     - 端点 URL 格式错误")
                
        print()
        
    except Exception as e:
        print(f"配置加载失败: {e}")
        print("请确保 config.yaml 文件存在且格式正确")

if __name__ == "__main__":
    test_storage_connection()

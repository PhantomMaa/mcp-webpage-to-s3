#!/usr/bin/env python3
"""自动修复配置文件中的 region 和 endpoint 不匹配问题"""

import yaml
import os
import shutil
from datetime import datetime

def fix_config():
    """修复配置文件"""
    config_file = 'config.yaml'
    
    if not os.path.exists(config_file):
        print(f"错误: {config_file} 文件不存在")
        return False
    
    # 备份原配置文件
    backup_file = f'config.yaml.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(config_file, backup_file)
    print(f"已备份原配置文件到: {backup_file}")
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("当前配置:")
    print(f"  Region: {config['libcloud']['region']}")
    print(f"  Endpoint: {config['libcloud']['endpoint']}")
    
    # 检查并修复配置
    current_region = config['libcloud']['region']
    current_endpoint = config['libcloud']['endpoint']
    
    # 提供修复选项
    print("\n可用的修复选项:")
    print("1. 统一使用 ap-southeast-1 (新加坡) - 推荐")
    print("2. 统一使用 us-east-1 (美国东部) - 最稳定")
    print("3. 统一使用 ap-east-1 (香港) - 如果支持的话")
    
    choice = input("\n请选择修复方案 (1-3): ").strip()
    
    if choice == '1':
        # 使用新加坡区域
        config['libcloud']['region'] = 'ap-southeast-1'
        config['libcloud']['endpoint'] = 'https://s3.ap-southeast-1.amazonaws.com'
        print("已选择新加坡区域")
    elif choice == '2':
        # 使用美国东部区域
        config['libcloud']['region'] = 'us-east-1'
        config['libcloud']['endpoint'] = 'https://s3.amazonaws.com'
        print("已选择美国东部区域")
    elif choice == '3':
        # 使用香港区域
        config['libcloud']['region'] = 'ap-east-1'
        config['libcloud']['endpoint'] = 'https://s3.ap-east-1.amazonaws.com'
        print("已选择香港区域")
    else:
        print("无效选择，取消修复")
        return False
    
    # 写入修复后的配置
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n配置已修复:")
    print(f"  新 Region: {config['libcloud']['region']}")
    print(f"  新 Endpoint: {config['libcloud']['endpoint']}")
    
    print(f"\n请运行以下命令测试连接:")
    print("python debug_storage.py")
    
    return True

if __name__ == "__main__":
    fix_config()

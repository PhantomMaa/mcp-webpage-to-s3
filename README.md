# MCP Libcloud Server

一个基于 Python fastmcp 框架的 libcloud MCP 服务器，提供文件上传和 HTML 部署功能。

## 功能特性

- **deploy_html**: 部署 HTML 文件到远程存储
- **check_status**: 检查服务器状态和 libcloud 连接
- 支持多种云存储服务（S3、阿里云 OSS 等）
- 详细的错误处理和日志记录
- 完整的测试覆盖

## 安装要求

- Python 3.12+
- Apache Libcloud 库（已包含在依赖中）
- uv 包管理器

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 或者安装开发依赖
uv sync --extra dev
```

### 2. 依赖说明

项目使用 Apache Libcloud 库进行云存储操作。

### 3. 配置服务器

```bash
# 创建示例配置文件
python -m mcp_libcloud.server --create-sample-config

# 复制并编辑配置文件
cp config.yaml.sample config.yaml
# 编辑 config.yaml，填入你的云存储配置
```

### 4. 运行服务器

```bash
# 使用默认配置文件
python -m mcp_libcloud.server

# 或指定配置文件
python -m mcp_libcloud.server --config /path/to/config.yaml

# 或使用安装的命令
mcp-web-deploy --config config.yaml
```

## 配置说明

配置文件使用 YAML 格式，主要包含以下部分：

```yaml
libcloud:
  remote_name: "myremote"        # 远程存储名称
  remote_type: "s3"              # 存储类型：s3 或 oss
  access_key_id: "your_key"      # 访问密钥 ID
  secret_access_key: "your_secret" # 访问密钥
  endpoint: "https://s3.amazonaws.com" # 服务端点
  region: "us-east-1"            # 存储区域
  bucket: "your-bucket"          # 存储桶名称
  base_path: "uploads"           # 基础路径前缀

log_level: "INFO"                # 日志级别
```

## MCP 工具说明

### deploy_html

部署 HTML 文件到远程存储。

**参数：**
- `html_content` (str): HTML 文件内容
- `filename` (str, 可选): 文件名，默认为 "index.html"
- `remote_path` (str, 可选): 远程路径，默认为根目录

**返回：**
```json
{
  "success": true,
  "message": "HTML 文件部署成功",
  "filename": "index.html",
  "remote_path": "index.html",
  "url": "https://bucket.s3.amazonaws.com/uploads/index.html",
  "size_bytes": 1024
}
```

### check_status

检查服务器状态和 libcloud 连接。

**返回：**
```json
{
  "success": true,
  "server_status": "running",
  "storage_connection": "ok",
  "remote_name": "myremote",
  "bucket": "your-bucket",
  "base_path": "uploads"
}
```

## 开发

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=mcp_libcloud

# 运行特定测试文件
uv run pytest tests/test_config.py
```

### 项目结构

```
mcp-web-deploy/
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── libcloud_wrapper.py  # libcloud 包装器
│   └── server.py          # MCP 服务器主要实现
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_libcloud_wrapper.py
├── config.yaml.sample     # 示例配置文件
├── pyproject.toml         # 项目配置
└── README.md
```

## 支持的云存储服务

- **Amazon S3**: 设置 `remote_type: "s3"`
- **阿里云 OSS**: 设置 `remote_type: "oss"`
- 其他 S3 兼容存储服务

## 错误处理

所有工具在出现错误时都会返回详细的错误信息：

```json
{
  "success": false,
  "error": "详细的错误描述",
  "file_path": "/path/to/file"
}
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
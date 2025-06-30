# MCP Libcloud Server

一个基于 Python fastmcp 框架的 libcloud MCP 服务器，提供文件上传和 HTML 部署功能。

## 功能特性

- **deploy_html**: 部署 HTML 文件到远程存储
- 支持 S3 兼容的云存储服务
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
```

### 2. 依赖说明

项目使用 Apache Libcloud 库进行云存储操作。

### 3. 配置服务器

```bash
# 复制并编辑配置文件
cp config.yaml.sample config.yaml
# 编辑 config.yaml，填入你的云存储配置
```

### 4. 运行服务器

```bash
python -m mcp_libcloud.server

# 或使用安装的命令
mcp-web-deploy
```

## 配置说明

配置文件使用 YAML 格式，主要包含以下部分：

```yaml
mcp_server:
  port: 8001
  transport: stdio
  # transport: streamable-http
  # transport: sse

s3:
  access_key_id: your_access_key_id
  secret_access_key: your_secret_access_key
  bucket: your-bucket-name
  endpoint: https://s3.amazonaws.com
  base_url: https://your-bucket.s3.ap-southeast-1.amazonaws.com
  region: ap-southeast-1

log_level: INFO
```

## MCP 工具说明

### deploy_html

部署 HTML 文件到远程存储。

**参数：**
- `html_content` (str): HTML 文件内容

**返回：**
```json
{
  "success": true,
  "message": "HTML 文件部署成功",
  "remote_path": "index.html",
  "url": "https://bucket.s3.amazonaws.com/index.html",
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
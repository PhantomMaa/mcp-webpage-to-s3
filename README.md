# MCP WebPage To S3

一个基于 Python FastMCP 框架的 MCP 服务器，专注于将网页内容快速部署到 S3 存储服务。

可以看作腾讯 edgeone-pages 的基于 S3 的替代品。 

## 功能特性

- **deploy_html_to_s3**: 将 HTML 内容部署到 S3 存储并获取访问链接
- 支持所有 S3 兼容的云存储服务

## 安装要求

- Python 3.12+
- uv 包管理器（推荐）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd mcp-webpage-to-s3
```

### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

### 3. 配置服务器

```bash
# 复制并编辑配置文件
cp config.yaml.sample config.yaml
# 编辑 config.yaml，填入你的 S3 存储配置
```

### 4. 运行服务器

```bash
# 使用 Python 直接运行
python main.py

# 或使用安装的命令
mcp-webpage-to-s3

# 或使用 uvx 直接运行（推荐）
uvx mcp-webpage-to-s3
```

## 配置说明

项目支持两种配置方式：**环境变量**（优先）和**配置文件**。这分别适用于 stdio 和 容器化部署 两种模式。

### 方式 1：环境变量配置（stdio 模式下推荐）

```bash
# S3 存储配置
export MCP_S3_ACCESS_KEY="your_access_key_id"
export MCP_S3_SECRET_KEY="your_secret_access_key"
export MCP_S3_BUCKET="your-bucket-name"
export MCP_S3_ENDPOINT="https://s3.amazonaws.com"
export MCP_S3_BASE_URL="https://your-bucket.s3.ap-southeast-1.amazonaws.com"
export MCP_S3_REGION="ap-southeast-1"

# MCP 服务器配置
export MCP_TRANSPORT="stdio"
export MCP_PORT="8001"
export MCP_LOG_LEVEL="INFO"

# 运行服务器
uvx mcp-webpage-to-s3
```

### 方式 2：配置文件（容器化部署下推荐）

配置文件 `config.yaml` 使用 YAML 格式，包含以下配置项：

```yaml
# MCP 服务器配置
mcp_server:
  port: 8001                    # 服务器端口
  transport: stdio              # 传输协议：stdio, http, sse, streamable-http

# S3 存储配置
s3:
  access_key: your_access_key_id      # S3 访问密钥 ID
  secret_key: your_secret_access_key  # S3 访问密钥
  bucket: your-bucket-name            # S3 存储桶名称
  endpoint: https://s3.amazonaws.com  # S3 服务端点
  base_url: https://your-bucket.s3.ap-southeast-1.amazonaws.com  # 文件访问基础 URL
  region: ap-southeast-1              # 存储区域

# 日志级别
log_level: INFO
```

## MCP 工具说明

### deploy_html_to_s3

将 HTML 内容部署到 S3 存储并返回访问链接。

**参数：**
- `html_content` (str): 要部署的 HTML 文件内容

**返回示例：**
```json
{
  "success": true,
  "message": "HTML 文件部署成功",
  "url": "https://bucket.s3.amazonaws.com/abc123def456.html"
}
```

**错误返回示例：**
```json
{
  "success": false,
  "error": "S3 客户端未初始化，无法上传文件"
}
```

## 版本历史

- **v0.2.0**: 
  - ✨ 新增环境变量配置支持
  - 🔧 配置优先级：环境变量 > 配置文件
  - 📦 改进包构建和入口点配置
  - 🐳 优化 Docker 和 CI/CD 使用体验
- **v0.1.1**: 发布到 pypi
- **v0.1.0**: 初始版本，支持基本的 HTML 部署功能3、阿里云 OSS、腾讯云 COS 等）
- 自动生成唯一文件名，避免文件冲突
- 优化的 HTML 文件缓存和内容类型设置
- 支持多种传输协议（stdio、http、sse、streamable-http）

## 许可证

MIT License - 详见 LICENSE 文件

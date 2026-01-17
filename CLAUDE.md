# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此仓库中工作提供指导。

## 项目概述

这是一个基于 Python 的 MCP (Model Context Protocol) 服务器，用于将 HTML 内容部署到 S3 兼容的存储服务。项目使用 FastMCP 框架构建，提供单一工具 `deploy_html_to_s3` 用于上传 HTML 内容到 S3 存储，并自动生成唯一文件名。

## 常用开发命令

### 安装和设置
```bash
# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip 安装
pip install -e .
```

### 运行服务器
```bash
# 直接使用 Python 运行
python main.py

# 使用安装的命令
mcp-webpage-to-s3

# 使用 uvx（推荐）
uvx mcp-webpage-to-s3
```

### 测试
```bash
# 运行测试（如果有测试的话）
pytest

# 使用开发依赖运行
uv run pytest
```

### 代码质量
```bash
# 使用 Black 格式化代码（配置行长度 150）
black src/

# 类型检查（如果添加了 mypy）
mypy src/
```

### Docker
```bash
# 构建 Docker 镜像
docker build -t mcp-webpage-to-s3 .

# 运行容器
docker run -p 8001:8001 mcp-webpage-to-s3
```

## 架构概述

项目采用模块化架构，关注点清晰分离：

### 核心组件

- **`src/server.py`**: 使用 FastMCP 框架的主 MCP 服务器
  - 定义 `deploy_html_to_s3` 工具
  - 处理不同传输协议（stdio, http, sse, streamable-http）
  - 通过 `run_server()` 函数作为服务器入口点

- **`src/config.py`**: 使用 Pydantic 模型的配置管理
  - 支持环境变量（优先级高）和 YAML 配置文件
  - `S3Config`: S3 存储配置
  - `MCPServerConfig`: MCP 服务器传输和端口设置
  - `ServerConfig`: 主配置容器

- **`src/s3.py`**: 使用 boto3 的 S3 客户端包装器
  - `S3Client` 类处理文件上传到 S3 兼容存储
  - 支持自定义端点、区域和认证
  - 包含使用 `StorageError` 的适当错误处理

- **`src/deploy.py`**: HTML 部署逻辑
  - `upload_html_content()`: 创建临时 HTML 文件并上传到 S3
  - 设置适当的内容头（ContentType, CacheControl 等）
  - 自动清理临时文件

- **`src/logger.py`**: 使用 loguru 的日志设置

### 配置优先级

1. **环境变量**（最高优先级）- 推荐用于 stdio/MCP 客户端使用
2. **YAML 配置文件**（`config.yaml`）- 推荐用于容器化部署

### 关键环境变量
- `S3_ACCESS_KEY`, `S3_SECRET_KEY`: S3 凭证
- `S3_BUCKET`, `S3_ENDPOINT`, `S3_BASE_URL`: S3 设置
- `MCP_SERVER_TRANSPORT`: 传输协议（stdio, http, sse, streamable-http）
- `MCP_SERVER_PORT`: 非 stdio 传输的服务器端口
- `LOG_LEVEL`: 日志级别

### MCP 工具

**`deploy_html_to_s3`**:
- 输入: `html_content` (字符串) - 要部署的 HTML 内容
- 输出: 包含成功状态、消息和部署 URL 的 JSON
- 使用 nanoid 生成唯一的 16 字符文件名
- 为正确的浏览器渲染设置 HTML 特定的内容头

## 开发注意事项

- 需要 Python 3.12+
- 使用 `uv` 进行依赖管理（推荐）
- 基于 FastMCP 框架构建，支持 MCP 协议
- 使用 Pydantic 进行配置验证
- 支持所有 S3 兼容的存储服务（AWS S3、MinIO 等）
- 配置为 Black 格式化，行长度 150 字符
- 在 `pyproject.toml` 中配置入口点作为控制台脚本

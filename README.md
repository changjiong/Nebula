# Talos - AI Agent 平台

基于 FastAPI + React 的全栈 AI Agent 开发与管理平台。

## ✨ 功能特性

### 🤖 AI Agent 核心能力

- **智能对话** - 支持流式响应（SSE）的实时 AI 对话
- **思维链展示** - 透明展示 Agent 推理过程
- **多模型支持** - 兼容 OpenAI API 格式，支持 DeepSeek、OpenAI、SiliconFlow 等providers
- **Agent 管理** - 创建、配置和部署多种 AI Agent

### 🛠️ 工具与技能

- **Tools 管理** - 原子级可调用工具，支持 Native Function Calling (NFC)
- **Skills 管理** - 基于 DAG 的复杂工作流编排
- **数据标准化** - 数据标准表与字段映射管理

### 📊 监控与管理

- **任务监控** - 后台任务状态追踪
- **模型提供商管理** - 多 LLM 提供商配置
- **用户权限管理** - 基于角色的访问控制

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 用途 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com) | Python Web 框架 |
| [SQLModel](https://sqlmodel.tiangolo.com) | ORM 数据库交互 |
| [PostgreSQL](https://www.postgresql.org) | 关系型数据库 |
| [Alembic](https://alembic.sqlalchemy.org) | 数据库迁移 |
| [Pydantic](https://docs.pydantic.dev) | 数据验证与设置管理 |
| [uv](https://docs.astral.sh/uv/) | Python 包管理器 |

### 前端技术栈

| 技术 | 用途 |
|------|------|
| [React](https://react.dev) | UI 框架 |
| [TypeScript](https://www.typescriptlang.org/) | 类型安全的 JavaScript |
| [Vite](https://vitejs.dev) | 构建工具 |
| [TanStack Router](https://tanstack.com/router) | 路由管理 |
| [TanStack Query](https://tanstack.com/query) | 数据获取与缓存 |
| [Tailwind CSS](https://tailwindcss.com) | CSS 框架 |
| [shadcn/ui](https://ui.shadcn.com) | UI 组件库 |
| [Playwright](https://playwright.dev) | E2E 测试 |

### 基础设施

- 🐋 [Docker Compose](https://www.docker.com) - 容器化开发与部署
- 🔒 JWT 认证 - 安全的用户认证
- 📫 邮件发送 - 密码重置等邮件功能
- 📞 [Traefik](https://traefik.io) - 反向代理与 HTTPS
- 🏭 GitHub Actions - CI/CD 自动化

---

## 🚀 快速开始

### 环境要求

- [Docker](https://www.docker.com/) 及 Docker Compose
- [uv](https://docs.astral.sh/uv/) (用于本地后端开发)
- [Node.js](https://nodejs.org/) 22+ (用于本地前端开发)

### 启动开发环境

```bash
# 克隆项目
git clone <repository-url>
cd talos

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量

# 启动所有服务（带热重载）
docker compose watch
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 (Swagger) | http://localhost:8000/docs |
| 数据库管理 (Adminer) | http://localhost:8080 |
| Traefik 面板 | http://localhost:8090 |
| 邮件捕获 (MailCatcher) | http://localhost:1080 |

---

## ⚙️ AI 配置

### DeepSeek API 配置

1. 从 [DeepSeek 平台](https://platform.deepseek.com/) 获取 API Key
2. 在 `.env` 文件中配置：

```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

3. 重启后端服务：`docker compose restart backend`

### 切换 LLM 提供商

本项目兼容 OpenAI API 格式。切换其他提供商示例：

```bash
# OpenAI
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4

# SiliconFlow（国内替代）
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_BASE=https://api.siliconflow.cn/v1
LLM_MODEL=deepseek-ai/DeepSeek-V3
```

---

## 📁 项目结构

```
talos/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── agent/          # AI Agent 实现
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── llm/            # LLM 客户端与网关
│   │   ├── models/         # 数据库模型
│   │   ├── tools/          # 工具实现
│   │   └── engine/         # 执行引擎
│   ├── alembic/            # 数据库迁移
│   └── tests/              # 测试文件
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── routes/         # 页面路由
│   │   ├── components/     # UI 组件
│   │   ├── client/         # OpenAPI 客户端
│   │   ├── hooks/          # React Hooks
│   │   └── stores/         # 状态管理
│   └── tests/              # E2E 测试
├── docs/                   # 项目文档
├── scripts/                # 脚本工具
└── docker-compose.yml      # Docker 编排配置
```

---

## 📖 详细文档

- **后端开发**: [backend/README.md](./backend/README.md)
- **前端开发**: [frontend/README.md](./frontend/README.md)
- **部署指南**: [deployment.md](./deployment.md)
- **开发指南**: [development.md](./development.md)
- **实现计划**: [docs/implementation_plan.md](./docs/implementation_plan.md)

---

## 🔧 常用命令

### 后端开发

```bash
# 进入后端容器
docker compose exec backend bash

# 创建数据库迁移
alembic revision --autogenerate -m "描述信息"

# 应用数据库迁移
alembic upgrade head

# 运行测试
bash scripts/test.sh
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生成 OpenAPI 客户端
npm run generate-client

# 运行 E2E 测试
npx playwright test
```

### 代码质量

```bash
# 安装 pre-commit hooks
cd backend && uv run prek install -f

# 手动运行代码检查
uv run prek run --all-files
```

---

## 🔐 安全配置

部署前请确保修改以下环境变量：

- `SECRET_KEY` - 用于签名的密钥
- `FIRST_SUPERUSER_PASSWORD` - 超级管理员密码  
- `POSTGRES_PASSWORD` - 数据库密码

生成安全密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📄 许可证

本项目基于 MIT 许可证开源。

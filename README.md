# Nebula 星图

> 企业关系如星系般连接，从中发现高价值恒星（客户）

**银行对公关系营销拓客助手** - 基于 AI 的企业智能分析与客户价值发现系统

---

## ✨ 核心能力

### 🏢 企业洞察

- **企业信息查询** - 一句话查询企业工商、股权、财务等多维信息
- **科创能力评估** - 五维度科创评分，精准识别科创型企业
- **股权穿透分析** - 可视化股权关系图谱，识别实际控制人

### 🔗 关系挖掘

- **交易对手挖掘** - 基于核心客户发现其上下游优质企业
- **担保链分析** - 追踪担保关系网络，识别风险传导路径
- **关联企业图谱** - 发现隐性关联，拓展客户生态圈

### 🎯 精准营销

- **客户画像生成** - 自动生成企业全景画像报告
- **白名单筛选** - 智能筛选符合准入标准的潜在客户
- **营销话术建议** - 根据企业特征生成个性化营销策略

### � 智能交互

- **自然语言对话** - 用自然语言完成复杂查询与分析任务
- **思维链透明展示** - 展示 AI 分析推理过程，结果可追溯
- **多轮交互优化** - 通过追问澄清，精准理解业务意图

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
cd Nebula

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
Nebula/
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
docker compose exec backend bash scripts/tests-start.sh
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

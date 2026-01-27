# 贡献指南

本文档介绍 Nebula 星图项目的开发协作流程和部署规范。

---

## 🌿 分支策略

### 分支结构

```
master (生产环境)
   ↑
develop (测试环境)
   ↑
feature/* (功能开发)
bugfix/*  (问题修复)
```

| 分支 | 用途 | 保护规则 |
|------|------|---------|
| `master` | 生产环境代码 | 🔒 禁止直接推送，仅通过 PR 合并 |
| `develop` | 测试/预发布环境 | 🔒 禁止直接推送，仅通过 PR 合并 |
| `feature/*` | 新功能开发 | 开发者自由推送 |
| `bugfix/*` | Bug 修复 | 开发者自由推送 |

---

## 📝 开发流程

### 1. 开始新功能

```bash
# 确保本地 develop 是最新的
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/功能名称
```

### 2. 提交代码

```bash
# 添加变更
git add .

# 提交（遵循 Conventional Commits）
git commit -m "feat: 添加企业查询功能"

# 推送到远程
git push origin feature/功能名称
```

#### Commit 规范

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加科创评分模块` |
| `fix` | Bug 修复 | `fix: 修复登录验证问题` |
| `docs` | 文档更新 | `docs: 更新 API 文档` |
| `style` | 代码格式 | `style: 格式化代码` |
| `refactor` | 重构 | `refactor: 优化查询逻辑` |
| `test` | 测试 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |

### 3. 创建 Pull Request

1. 在 GitHub 创建 PR：`feature/xxx` → `develop`
2. 填写 PR 描述，说明改动内容
3. 指定 Reviewer（至少 1 人）
4. 等待 Review 通过后合并

### 4. 合并到 develop

- PR 通过后，由 Reviewer 或作者合并
- 合并后 **自动部署到 Staging 环境**

### 5. 发布到生产

```bash
# 确认 Staging 测试通过后
git checkout master
git pull origin master
git merge develop
git push origin master

# 或通过 GitHub Release 发布
```

---

## 🚀 部署架构

### 环境规划

| 环境 | 分支 | 域名 | 部署触发 |
|------|------|------|---------|
| Production | `master` | `nebula.example.com` | 推送/Release |
| Staging | `develop` | `staging.nebula.example.com` | 推送 |
| Local | - | `localhost:5173` | 手动启动 |

### 自动部署流程

```
代码推送 → GitHub Webhook → Coolify 接收 → 自动构建 → 部署上线
```

---

## 🔧 Coolify 部署配置

### 前置条件

- 一台安装了 [Coolify](https://coolify.io) 的 VPS
- GitHub 仓库访问权限
- 域名（可选，也可使用 IP）

### 配置步骤

#### 1. 创建 Coolify 项目

1. 登录 Coolify 管理面板
2. 点击 **+ Add Resource** → **Application**
3. 选择 **Docker Compose**
4. 连接 GitHub 并选择本仓库

#### 2. 配置构建参数

| 配置项 | Production | Staging |
|--------|------------|---------|
| Branch | `master` | `develop` |
| Build Pack | Docker Compose | Docker Compose |
| Docker Compose File | `docker-compose.coolify.yml` | `docker-compose.coolify.yml` |

> **注意**: `docker-compose.coolify.yml` 是专为 Coolify 优化的配置文件，已移除 Traefik 标签（Coolify 自动处理 SSL/代理）。

#### 3. 配置环境变量

在 Coolify 的 **Environment Variables** 中添加：

```bash
# 必填项
SECRET_KEY=<生成的随机密钥>
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=<管理员密码>
POSTGRES_PASSWORD=<数据库密码>
ENVIRONMENT=production  # 或 staging

# AI 模型配置
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 可选
DOMAIN=nebula.example.com
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=
```

> 生成密钥命令：`python -c "import secrets; print(secrets.token_urlsafe(32))"`

#### 4. 启用自动部署

1. 在 Coolify 应用设置中开启 **Auto Deploy**
2. Coolify 会自动配置 GitHub Webhook
3. 验证：GitHub 仓库 Settings → Webhooks 应有 Coolify 的记录

#### 5. 配置域名

本项目包含多个服务，需要在 Coolify 中分别配置域名：

| 服务 | 域名示例 | 端口 | 说明 |
|------|----------|------|------|
| **frontend** | `dashboard.nebula.example.com` | 80 | 用户界面 |
| **backend** | `api.nebula.example.com` | 8000 | API 服务 |
| **adminer** (可选) | `adminer.nebula.example.com` | 8080 | 数据库管理 |

配置步骤：
1. 在 Coolify 应用 → **Settings** → **General**
2. 找到对应服务的配置区域
3. 添加域名和对应的内部端口
4. Coolify 会自动申请 Let's Encrypt SSL 证书

---

## 💻 本地开发

### 环境要求

- Docker & Docker Compose
- Node.js 22+
- Python 3.12+ / uv

### 启动开发环境

```bash
# 克隆项目
git clone git@github.com:your-org/nebula.git
cd nebula

# 复制环境变量
cp .env.example .env
# 编辑 .env 配置必要变量

# 启动所有服务（带热重载）
docker compose watch
```

### 本地访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 数据库管理 | http://localhost:8080 |

---

## 🔍 代码审查规范

### Review 检查清单

- [ ] 代码逻辑正确，无明显 Bug
- [ ] 遵循项目代码风格
- [ ] 有必要的注释和文档
- [ ] 无敏感信息泄露（API Key、密码等）
- [ ] 数据库变更有对应的 Migration

### 审查反馈

- 使用 GitHub Review 功能
- 小问题用 Comment
- 必须修改用 Request Changes
- 通过后 Approve

---

## 📋 发布检查清单

发布到生产环境前确认：

- [ ] Staging 环境测试通过
- [ ] 数据库 Migration 已验证
- [ ] 环境变量配置完整
- [ ] 关键功能手动验证
- [ ] 团队成员知悉发布

---

## ❓ 常见问题

### Q: Coolify 部署失败怎么办？

1. 检查 Coolify 的 Build Logs
2. 确认环境变量配置正确
3. 检查 docker-compose.yml 语法
4. 查看 GitHub Webhook 投递记录

### Q: 本地和线上数据库结构不一致？

```bash
# 进入后端容器
docker compose exec backend bash

# 生成新的 Migration
alembic revision --autogenerate -m "描述"

# 应用 Migration
alembic upgrade head
```

### Q: 如何回滚部署？

在 Coolify 中：
1. 进入应用 → Deployments
2. 找到上一个成功的部署
3. 点击 **Redeploy**

---

## 📞 联系方式

如有问题，请联系项目维护者或在 GitHub Issues 中提问。

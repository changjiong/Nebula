# 多人并行开发指南

## Worktree 目录

每个目录是一个独立的工作空间，对应一个功能分支：

| 目录 | 分支 | 开发内容 |
|------|------|----------|
| `/home/lsnn/github/full-stack-fastapi-template` | master | 主分支（合并用） |
| `/home/lsnn/github/agent-portal-engine` | feature/backend-engine | LangGraph 引擎 |
| `/home/lsnn/github/agent-portal-agents` | feature/backend-agents | Agent 定义框架 |
| `/home/lsnn/github/agent-portal-adapters` | feature/backend-adapters | 外部服务适配器 |
| `/home/lsnn/github/agent-portal-api` | feature/backend-api | API 端点 |
| `/home/lsnn/github/agent-portal-frontend-chat` | feature/frontend-chat | 对话界面 |
| `/home/lsnn/github/agent-portal-frontend-components` | feature/frontend-components | 动态组件 |

## 并行开发流程

1. **打开新窗口**：在 IDE 中打开对应目录
2. **启动 Agent**：每个窗口启动独立的 AI Agent
3. **独立开发**：每个 Agent 专注于自己分支的功能
4. **提交代码**：在各自分支提交
5. **合并到 master**：所有开发完成后，切回主项目合并

## 合并命令（在主项目执行）

```bash
cd /home/lsnn/github/full-stack-fastapi-template
git merge feature/backend-engine
git merge feature/backend-agents
git merge feature/backend-adapters
git merge feature/backend-api
git merge feature/frontend-chat
git merge feature/frontend-components
```

## 清理 Worktree（合并完成后）

```bash
cd /home/lsnn/github/full-stack-fastapi-template
git worktree remove ../agent-portal-engine
git worktree remove ../agent-portal-agents
git worktree remove ../agent-portal-adapters
git worktree remove ../agent-portal-api
git worktree remove ../agent-portal-frontend-chat
git worktree remove ../agent-portal-frontend-components
```

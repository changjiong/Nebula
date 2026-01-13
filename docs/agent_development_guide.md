# Agent 开发指南

> 本指南介绍如何在 Unified Agent Portal 中开发新的业务 Agent。

## 目录结构

每个 Agent 位于 `backend/app/agent/` 目录下：

```
backend/app/agent/
├── __init__.py          # 模块入口
├── base.py              # BaseAgent, AgentConfig
├── registry.py          # @register_agent 装饰器
├── _template/           # 开发模板
│   ├── config.yaml      # 配置模板
│   └── handler.py       # 处理器模板
└── enterprise_resolver/ # 示例 Agent
    ├── __init__.py
    ├── config.yaml      # Agent 配置
    └── handler.py       # 业务逻辑
```

## 快速开始

### 1. 复制模板

```bash
cp -r backend/app/agent/_template backend/app/agent/my_agent
```

### 2. 编辑 config.yaml

```yaml
name: my_agent
version: "1.0.0"
description: "我的 Agent 描述"

input:
  - name: query
    type: string
    required: true
    description: "用户查询"

output:
  - name: result
    type: object
    description: "查询结果"

services:
  - name: data_warehouse
    endpoint: /api/v1/query
    method: POST
    timeout: 30

metadata:
  category: "分析"
  frontend_component: "entity_card"
```

### 3. 实现 handler.py

```python
from app.agent.base import AgentInput, AgentOutput, BaseAgent
from app.agent.registry import register_agent

@register_agent
class MyAgent(BaseAgent):
    name = "my_agent"
    description = "我的 Agent"

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        query = input_data.query  # type: ignore

        # 调用外部服务
        service_config = self.get_service_config("data_warehouse")
        # ... 实现业务逻辑

        return AgentOutput(
            success=True,
            data={"result": "..."}
        )
```

### 4. 注册 Agent

在 `__init__.py` 中导入 handler：

```python
from app.agent.my_agent.handler import MyAgent
```

## 核心类

### AgentConfig

从 `config.yaml` 自动加载：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | Agent 唯一标识 |
| `input` | list | 输入参数定义 |
| `output` | list | 输出结构定义 |
| `services` | list | 外部服务配置 |

### BaseAgent

抽象基类，必须实现 `execute()` 方法：

```python
class BaseAgent(ABC):
    name: str           # Agent 名称
    description: str    # Agent 描述
    
    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """执行 Agent 逻辑"""
        pass
    
    def get_service_config(self, name: str) -> AgentServiceConfig | None:
        """获取服务配置"""
        pass
    
    def validate_input(self, data: dict) -> list[str]:
        """验证输入参数"""
        pass
```

### AgentRegistry

Agent 注册表：

```python
from app.agent import AgentRegistry

# 获取 Agent 类
agent_cls = AgentRegistry.get("my_agent")

# 获取单例实例
agent = AgentRegistry.get_instance("my_agent")

# 列出所有 Agent
for name, cls in AgentRegistry.list_agents():
    print(f"{name}: {cls}")

# 自动发现
from app.agent.registry import discover_agents
discovered = discover_agents()
```

## 前端组件映射

在 `config.yaml` 的 `metadata.frontend_component` 中指定：

| 组件类型 | 用途 |
|---------|------|
| `entity_card` | 单个实体卡片 |
| `candidate_list` | 候选列表（需选择） |
| `data_table` | 数据表格 |
| `score_card` | 评分卡片 |
| `relation_graph` | 关系图谱 |
| `tree_view` | 树状结构 |
| `markdown_content` | 富文本内容 |
| `action_buttons` | 操作按钮组 |

## 测试

```bash
cd backend
uv run pytest tests/agent/ -v
```

## 最佳实践

1. **Mock 模式**：开发时使用适配器的 mock 模式
2. **输入验证**：使用 `validate_input()` 验证参数
3. **错误处理**：返回 `AgentOutput(success=False, error="...")` 
4. **日志记录**：使用 `logging` 模块记录关键步骤

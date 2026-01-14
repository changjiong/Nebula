# 交易对手挖掘 Agent (Counterparty Mining)

## 功能说明

基于目标企业挖掘上下游交易对手，支持关系图谱可视化。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enterprise_name | string | - | 目标企业名称 |
| credit_code | string | - | 统一社会信用代码 |
| direction | string | "both" | upstream/downstream/both |
| depth | int | 2 | 挖掘深度 (1-3) |
| limit | int | 20 | 结果数量限制 |

## 使用示例

```python
from app.agent.counterparty_mining import CounterpartyMiningAgent
from app.agent.counterparty_mining.handler import CounterpartyMiningInput

agent = CounterpartyMiningAgent()
output = await agent.execute(
    CounterpartyMiningInput(
        enterprise_name="华为技术有限公司",
        direction="both",
        depth=2,
        limit=10,
    )
)

print(output.counterparties)  # 交易对手列表
print(output.graph_data)      # 关系图谱数据
print(output.statistics)      # 统计信息
```

## 输出格式

```json
{
  "success": true,
  "counterparties": [
    {
      "name": "华强供应链有限公司",
      "credit_code": "91440300...",
      "relation_type": "upstream",
      "relation_desc": "原材料供应",
      "strength": 0.85,
      "depth": 1
    }
  ],
  "graph_data": {
    "nodes": [
      {"id": "target", "name": "华为技术", "is_target": true},
      {"id": "cp_0", "name": "华强供应链", "type": "upstream"}
    ],
    "edges": [
      {"source": "cp_0", "target": "target", "relation": "供应"}
    ]
  },
  "statistics": {
    "upstream_count": 3,
    "downstream_count": 4,
    "total_count": 7
  }
}
```

## 前端组件

输出的 `graph_data` 可直接用于 `RelationGraph` 组件渲染。

## TODO

- [ ] 集成 data_warehouse 供应链数据
- [ ] 集成 external_api 工商关系查询

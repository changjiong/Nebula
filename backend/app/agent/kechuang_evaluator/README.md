# 科创评价 Agent (Kechuang Evaluator)

## 功能说明

对企业进行科创五维评分分析：

| 维度 | 英文 | 权重 | 评分依据 |
|------|------|------|---------|
| 创新力 | innovation | 30% | 专利数量、研发投入、技术团队 |
| 成长性 | growth | 25% | 营收增长、员工增长 |
| 稳定性 | stability | 25% | 运营年限、财务健康度 |
| 合作度 | cooperation | 20% | 产学研合作、政府关系 |
| 综合 | overall | - | 加权平均 |

## 评级标准

- **A级**: 综合 >= 85
- **B级**: 综合 >= 70
- **C级**: 综合 >= 55
- **D级**: 综合 < 55

## 使用示例

```python
from app.agent.kechuang_evaluator import KechuangEvaluatorAgent
from app.agent.kechuang_evaluator.handler import KechuangEvaluatorInput

agent = KechuangEvaluatorAgent()
output = await agent.execute(
    KechuangEvaluatorInput(
        enterprise_name="华为技术有限公司",
        include_details=True,
    )
)

print(output.scores)      # ScoreBreakdown
print(output.radar_data)  # 雷达图数据
print(output.rank)        # "A"
```

## 输出格式

```json
{
  "success": true,
  "scores": {
    "innovation": 85.5,
    "growth": 78.2,
    "stability": 82.0,
    "cooperation": 75.0,
    "overall": 80.9
  },
  "radar_data": [
    {"axis": "创新力", "value": 85.5},
    {"axis": "成长性", "value": 78.2},
    ...
  ],
  "rank": "B",
  "analysis": "华为技术有限公司 综合评级为 B 级..."
}
```

## TODO

- [ ] 集成 model_factory 评分模型
- [ ] 集成 data_warehouse 特征数据

# Enterprise Resolver Agent

企业主体识别 Agent - 从模糊的企业名称识别出准确的企业实体

## 配置

```yaml
id: "enterprise_resolver"
name: "企业主体识别"
version: "1.0.0"
category: "risk_assessment"
status: "active"

description: |
  根据用户提供的企业名称（可能是简称或模糊描述），
  识别出准确的企业主体信息，包括统一社会信用代码、法定代表人等。

inputs:
  - name: query
    type: string
    description: "企业名称（支持模糊匹配）"
    required: true
    
outputs:
  json_schema:
    type: object
    properties:
      name:
        type: string
        description: "企业全称"
      credit_code:
        type: string
        description: "统一社会信用代码"
      legal_person:
        type: string
        description: "法定代表人"
      registered_capital:
        type: string
        description: "注册资本"
      region:
        type: string
        description: "注册地区"
      status:
        type: string
        description: "企业状态"

service_calls:
  - name: search_enterprise
    service_type: data_warehouse
    service_id: "enterprise_search"
    params_mapping:
      name: "${inputs.query}"
    result_mapping: "$"

execution_mode: "realtime"

output_component: "entity_card"

permissions:
  visibility: "public"
```

## 示例对话

**用户**: "帮我查一下先进数通"

**Agent 响应**:
1. 调用数仓API搜索企业
2. 如果唯一匹配，直接返回企业卡片
3. 如果多个匹配，使用反问模式让用户选择

输出组件：`entity_card`

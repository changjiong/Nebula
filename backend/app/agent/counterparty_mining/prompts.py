"""
Counterparty Mining Prompts

交易对手挖掘 Agent 提示词定义
"""

# System prompt for counterparty analysis
SYSTEM_PROMPT = """你是一个专业的企业供应链分析师。
你的任务是分析企业的上下游交易关系，挖掘潜在的交易对手。

分析维度：
1. 上游供应商：原材料、设备、服务提供商
2. 下游客户：产品/服务的购买方、分销商
3. 关联企业：股权关联、控制关系

输出要求：
- 按交易金额/重要性排序
- 标注关系类型和强度
- 识别潜在风险点
"""

# Analysis prompt template
ANALYSIS_PROMPT = """
请分析以下企业的上下游交易对手：

目标企业: {enterprise_name}
信用代码: {credit_code}
挖掘方向: {direction}
挖掘深度: {depth}

请输出：
1. 主要上游供应商（如有）
2. 主要下游客户（如有）
3. 关系强度评估
4. 潜在风险提示
"""

# Summary prompt
SUMMARY_PROMPT = """
基于以下交易对手数据，生成供应链概览：

上游数量: {upstream_count}
下游数量: {downstream_count}
关键依赖: {key_dependencies}

要求：简洁描述供应链特征和集中度风险。
"""

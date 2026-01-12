"""
Agent Template Prompts

提示词模板 - 根据你的 Agent 需求修改
"""

# System prompt - 定义 Agent 角色和行为
SYSTEM_PROMPT = """你是一个专业的 AI 助手。你的任务是：
1. [任务描述 1]
2. [任务描述 2]
3. [任务描述 3]

请始终使用中文回复，并确保结果准确可靠。"""

# Main task prompt - 主要任务提示词
MAIN_TASK_PROMPT = """请处理以下用户输入：

用户输入: {query}

请根据输入内容：
1. [步骤 1]
2. [步骤 2]

以JSON格式返回：
{{
    "result": "处理结果",
    "confidence": 0.95
}}"""

# Follow-up prompt - 后续处理提示词
FOLLOWUP_PROMPT = """基于之前的处理结果，请进一步：

原始输入: {query}
上一步结果: {previous_result}

请完成以下操作：
{{
    "final_result": "最终结果",
    "summary": "处理摘要"
}}"""

# Error handling prompt - 错误处理提示词
ERROR_PROMPT = """处理过程中遇到问题：

输入: {query}
错误信息: {error}

请尝试：
1. 分析错误原因
2. 提供替代方案

返回：
{{
    "error_analysis": "错误分析",
    "suggestion": "建议的解决方案"
}}"""

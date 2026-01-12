"""
Enterprise Resolver Prompts

提示词模板用于企业主体识别任务
"""

# System prompt for the agent
SYSTEM_PROMPT = """你是一个专业的企业主体识别助手。你的任务是：
1. 分析用户输入的企业相关信息
2. 识别其中的企业名称、统一社会信用代码等关键信息
3. 进行模糊匹配和消歧
4. 返回最相关的企业实体列表

请始终使用中文回复，并确保识别结果准确可靠。"""

# Prompt for entity extraction from user query
EXTRACTION_PROMPT = """请从以下用户输入中提取企业相关信息：

用户输入: {query}

请识别并提取：
1. 企业名称（全称或简称）
2. 统一社会信用代码（如有）
3. 其他关键词

以JSON格式返回：
{{
    "enterprise_names": ["提取的企业名称列表"],
    "credit_codes": ["提取的信用代码列表"],
    "keywords": ["其他关键词"],
    "query_type": "name|code|keyword"
}}"""

# Prompt for disambiguation when multiple matches found
DISAMBIGUATION_PROMPT = """找到多个匹配的企业实体，请帮助用户选择：

用户原始查询: {query}

匹配结果:
{matches}

请分析每个匹配结果与用户查询的相关性，并按相关性排序返回：
{{
    "ranked_results": [
        {{
            "index": 0,
            "confidence": 0.95,
            "reason": "排序理由"
        }}
    ],
    "disambiguation_needed": true/false,
    "clarification_question": "如需要用户进一步澄清，提供问题"
}}"""

# Prompt for result formatting
FORMAT_RESULT_PROMPT = """请将以下企业信息格式化为用户友好的输出：

企业信息:
{enterprise_data}

请生成简洁明了的描述，包含：
1. 企业全称
2. 统一社会信用代码
3. 主要业务范围
4. 状态信息

输出格式要求：markdown 格式，便于前端展示。"""

# Prompt for confidence scoring
CONFIDENCE_PROMPT = """请评估以下匹配结果的置信度：

用户查询: {query}
匹配企业: {enterprise_name}
匹配方式: {match_type}

请返回 0-1 之间的置信度分数，并说明理由：
{{
    "confidence": 0.85,
    "factors": [
        {{"factor": "名称完全匹配", "weight": 0.5}},
        {{"factor": "行业相关", "weight": 0.3}}
    ]
}}"""

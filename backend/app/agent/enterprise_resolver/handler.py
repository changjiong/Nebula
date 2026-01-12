"""
Enterprise Resolver Handler

企业主体识别 Agent 业务逻辑实现
"""

import logging
import re
from typing import Any

from pydantic import BaseModel, Field

from app.agent.base import AgentInput, AgentOutput, BaseAgent
from app.agent.registry import register_agent

logger = logging.getLogger(__name__)


class EnterpriseResolverInput(AgentInput):
    """Enterprise resolver input schema."""

    query: str = Field(..., description="用户输入的企业名称或关键词")
    limit: int = Field(default=10, description="返回结果数量限制")
    min_confidence: float = Field(default=0.5, description="最小置信度阈值")


class EnterpriseInfo(BaseModel):
    """Enterprise information model."""

    name: str = Field(..., description="企业名称")
    credit_code: str = Field(default="", description="统一社会信用代码")
    legal_representative: str = Field(default="", description="法定代表人")
    registered_capital: str = Field(default="", description="注册资本")
    status: str = Field(default="", description="经营状态")
    industry: str = Field(default="", description="所属行业")
    confidence: float = Field(default=0.0, description="匹配置信度")


class EnterpriseResolverOutput(AgentOutput):
    """Enterprise resolver output schema."""

    enterprises: list[EnterpriseInfo] = Field(
        default_factory=list, description="识别到的企业列表"
    )
    total_count: int = Field(default=0, description="匹配总数")
    query_type: str = Field(default="keyword", description="查询类型")


@register_agent
class EnterpriseResolverAgent(BaseAgent):
    """企业主体识别 Agent.

    解析用户输入，识别企业实体，支持：
    - 企业名称模糊匹配
    - 统一社会信用代码精确匹配
    - 关键词搜索
    """

    name = "enterprise_resolver"
    description = "企业主体识别 Agent - 解析用户输入识别企业实体"
    version = "1.0.0"

    # Credit code regex pattern (18 characters)
    CREDIT_CODE_PATTERN = re.compile(r"^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$")

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute enterprise resolution logic.

        Args:
            input_data: Input containing query, limit, and min_confidence

        Returns:
            Output containing matched enterprises
        """
        # Parse input
        if isinstance(input_data, EnterpriseResolverInput):
            query = input_data.query
            limit = input_data.limit
            min_confidence = input_data.min_confidence
        else:
            # Handle generic AgentInput
            query = getattr(input_data, "query", "")
            limit = getattr(input_data, "limit", 10)
            min_confidence = getattr(input_data, "min_confidence", 0.5)

        if not query:
            return EnterpriseResolverOutput(
                success=False,
                error="Query cannot be empty",
            )

        try:
            # Step 1: Determine query type
            query_type = self._detect_query_type(query)
            logger.info(f"Query type detected: {query_type} for query: {query}")

            # Step 2: Search for enterprises
            enterprises = await self._search_enterprises(
                query=query,
                query_type=query_type,
                limit=limit,
            )

            # Step 3: Filter by confidence threshold
            filtered = [e for e in enterprises if e.confidence >= min_confidence]

            return EnterpriseResolverOutput(
                success=True,
                enterprises=filtered,
                total_count=len(filtered),
                query_type=query_type,
                data={
                    "original_query": query,
                    "total_matches": len(enterprises),
                    "filtered_count": len(filtered),
                },
            )

        except Exception as e:
            logger.error(f"Enterprise resolution failed: {e}")
            return EnterpriseResolverOutput(
                success=False,
                error=str(e),
            )

    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query.

        Args:
            query: User input query

        Returns:
            Query type: "code", "name", or "keyword"
        """
        # Clean query
        cleaned = query.strip().upper()

        # Check if it's a credit code
        if self.CREDIT_CODE_PATTERN.match(cleaned):
            return "code"

        # Check if it looks like an enterprise name
        name_indicators = ["公司", "集团", "有限", "股份", "企业", "厂", "店"]
        if any(indicator in query for indicator in name_indicators):
            return "name"

        # Default to keyword search
        return "keyword"

    async def _search_enterprises(
        self,
        query: str,
        query_type: str,
        limit: int,
    ) -> list[EnterpriseInfo]:
        """Search for enterprises based on query.

        Args:
            query: Search query
            query_type: Type of query
            limit: Maximum results to return

        Returns:
            List of matched enterprises

        Note:
            This is a placeholder implementation.
            In production, this would call external services.
        """
        # TODO: Integrate with actual services
        # - Call model_factory for NER
        # - Call data_warehouse for search
        # - Call external_api for verification

        # Placeholder: Return mock data for demonstration
        mock_results = await self._get_mock_results(query, query_type, limit)
        return mock_results

    async def _get_mock_results(
        self,
        query: str,
        query_type: str,
        limit: int,
    ) -> list[EnterpriseInfo]:
        """Get mock results for demonstration.

        In production, this should be replaced with actual service calls.
        """
        # Return empty list in production mode
        # This is just for testing/demonstration
        mock_data: list[dict[str, Any]] = []

        if query_type == "code":
            # Credit code search returns exact match
            mock_data = [
                {
                    "name": "示例科技有限公司",
                    "credit_code": query.upper(),
                    "legal_representative": "张三",
                    "registered_capital": "1000万人民币",
                    "status": "存续",
                    "industry": "科技推广和应用服务业",
                    "confidence": 1.0,
                }
            ]
        elif "科技" in query or "技术" in query:
            mock_data = [
                {
                    "name": f"{query}科技有限公司",
                    "credit_code": "91110000MA00ABCD12",
                    "legal_representative": "李四",
                    "registered_capital": "500万人民币",
                    "status": "存续",
                    "industry": "科技推广和应用服务业",
                    "confidence": 0.85,
                },
                {
                    "name": f"{query}技术服务有限公司",
                    "credit_code": "91110000MA00EFGH34",
                    "legal_representative": "王五",
                    "registered_capital": "200万人民币",
                    "status": "存续",
                    "industry": "信息技术服务业",
                    "confidence": 0.72,
                },
            ]

        return [EnterpriseInfo(**item) for item in mock_data[:limit]]

    async def call_ner_model(self, text: str) -> dict[str, Any]:
        """Call NER model for entity extraction.

        Args:
            text: Input text for NER

        Returns:
            Extracted entities

        Note:
            Placeholder for model_factory integration.
        """
        # TODO: Implement actual model factory call
        service_config = self.get_service_config("model_factory")
        if service_config:
            logger.info(f"Would call model: {service_config.model}")

        return {
            "entities": [],
            "raw_text": text,
        }

    async def search_data_warehouse(
        self, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Search data warehouse for enterprises.

        Args:
            params: Search parameters

        Returns:
            Search results

        Note:
            Placeholder for data_warehouse adapter integration.
        """
        # TODO: Implement actual data warehouse call
        service_config = self.get_service_config("data_warehouse")
        if service_config:
            logger.info(f"Would call endpoint: {service_config.endpoint}")

        return []

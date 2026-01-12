"""
Agent Template Handler

业务逻辑模板 - 复制并修改以实现你的 Agent

使用步骤:
1. 复制 _template 目录到新目录 (如 my_agent/)
2. 修改 config.yaml 中的配置
3. 修改 prompts.py 中的提示词
4. 实现 handler.py 中的业务逻辑
5. 更新 __init__.py 导出你的 Agent 类
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

from app.agent.base import AgentInput, AgentOutput, BaseAgent

# TODO: 取消注释以启用自动注册
# from app.agent.registry import register_agent

logger = logging.getLogger(__name__)


class TemplateInput(AgentInput):
    """Template agent input schema.

    TODO: 根据 config.yaml 中的 input 定义修改
    """

    query: str = Field(..., description="主要输入参数")
    options: dict[str, Any] = Field(default_factory=dict, description="可选配置")


class TemplateResult(BaseModel):
    """Template result model.

    TODO: 根据业务需求定义结果模型
    """

    value: str = Field(..., description="结果值")
    score: float = Field(default=0.0, description="评分")


class TemplateOutput(AgentOutput):
    """Template agent output schema.

    TODO: 根据 config.yaml 中的 output 定义修改
    """

    result: TemplateResult | None = Field(default=None, description="处理结果")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


# TODO: 取消注释以启用自动注册
# @register_agent
class TemplateAgent(BaseAgent):
    """Template Agent.

    TODO: 修改类名和描述

    功能说明:
    - [功能 1]
    - [功能 2]
    """

    # TODO: 修改为你的 Agent 标识符
    name = "template_agent"
    description = "Agent 模板 - 请修改此描述"
    version = "1.0.0"

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute agent logic.

        TODO: 实现你的业务逻辑

        Args:
            input_data: Input containing query and options

        Returns:
            Output containing result and metadata
        """
        # Parse input
        if isinstance(input_data, TemplateInput):
            query = input_data.query
            options = input_data.options
        else:
            query = getattr(input_data, "query", "")
            options = getattr(input_data, "options", {})

        if not query:
            return TemplateOutput(
                success=False,
                error="Query cannot be empty",
            )

        try:
            # TODO: 实现你的业务逻辑
            # Step 1: 预处理
            processed = await self._preprocess(query, options)

            # Step 2: 主要处理
            result = await self._process(processed)

            # Step 3: 后处理
            final_result = await self._postprocess(result)

            return TemplateOutput(
                success=True,
                result=final_result,
                metadata={
                    "query": query,
                    "processed": True,
                },
            )

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return TemplateOutput(
                success=False,
                error=str(e),
            )

    async def _preprocess(
        self, query: str, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Preprocess input.

        TODO: 实现预处理逻辑
        """
        return {
            "query": query,
            "options": options,
        }

    async def _process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Main processing logic.

        TODO: 实现主要处理逻辑，可能包括:
        - 调用 model_factory
        - 调用 data_warehouse
        - 调用 external_api
        """
        # Example: Get service config
        model_config = self.get_service_config("model_factory")
        if model_config:
            logger.info(f"Model: {model_config.model}")

        return {
            "processed": True,
            "data": data,
        }

    async def _postprocess(self, result: dict[str, Any]) -> TemplateResult:
        """Postprocess result.

        TODO: 实现后处理逻辑
        """
        return TemplateResult(
            value=str(result),
            score=1.0,
        )

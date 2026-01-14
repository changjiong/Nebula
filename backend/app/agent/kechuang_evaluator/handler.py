"""
Kechuang Evaluator Handler

科创评价 Agent 业务逻辑实现
"""

import logging
import random
from typing import Any

from pydantic import BaseModel, Field

from app.agent.base import AgentInput, AgentOutput, BaseAgent
from app.agent.registry import register_agent

logger = logging.getLogger(__name__)


class KechuangEvaluatorInput(AgentInput):
    """Kechuang evaluator input schema."""

    enterprise_name: str = Field(default="", description="企业名称")
    credit_code: str = Field(default="", description="统一社会信用代码")
    enterprise_id: str = Field(default="", description="企业ID")
    include_details: bool = Field(default=True, description="是否返回详细评分依据")


class ScoreBreakdown(BaseModel):
    """Score breakdown for each dimension."""

    innovation: float = Field(..., description="创新力评分 (0-100)")
    growth: float = Field(..., description="成长性评分 (0-100)")
    stability: float = Field(..., description="稳定性评分 (0-100)")
    cooperation: float = Field(..., description="合作度评分 (0-100)")
    overall: float = Field(..., description="综合评分 (0-100)")


class RadarDataPoint(BaseModel):
    """Single data point for radar chart."""

    axis: str = Field(..., description="维度名称")
    value: float = Field(..., description="评分值")


class KechuangEvaluatorOutput(AgentOutput):
    """Kechuang evaluator output schema."""

    scores: ScoreBreakdown | None = Field(default=None, description="五维评分")
    radar_data: list[RadarDataPoint] = Field(
        default_factory=list, description="雷达图数据"
    )
    analysis: str = Field(default="", description="综合分析说明")
    rank: str = Field(default="", description="评级等级")
    enterprise_name: str = Field(default="", description="企业名称")


@register_agent
class KechuangEvaluatorAgent(BaseAgent):
    """科创评价 Agent.

    对企业进行科创五维评分：
    - 创新力 (innovation)
    - 成长性 (growth)
    - 稳定性 (stability)
    - 合作度 (cooperation)
    - 综合 (overall)
    """

    name = "kechuang_evaluator"
    description = "科创评价 Agent - 对企业进行科创五维评分"
    version = "1.0.0"

    # Score weights for overall calculation
    WEIGHTS = {
        "innovation": 0.30,
        "growth": 0.25,
        "stability": 0.25,
        "cooperation": 0.20,
    }

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute kechuang evaluation logic.

        Args:
            input_data: Input containing enterprise info

        Returns:
            Output containing scores and analysis
        """
        # Parse input
        if isinstance(input_data, KechuangEvaluatorInput):
            enterprise_name = input_data.enterprise_name
            credit_code = input_data.credit_code
            include_details = input_data.include_details
        else:
            enterprise_name = getattr(input_data, "enterprise_name", "")
            credit_code = getattr(input_data, "credit_code", "")
            include_details = getattr(input_data, "include_details", True)

        # Validate input
        if not enterprise_name and not credit_code:
            return KechuangEvaluatorOutput(
                success=False,
                error="必须提供企业名称或统一社会信用代码",
            )

        try:
            # Step 1: Get enterprise features
            features = await self._get_enterprise_features(
                enterprise_name, credit_code
            )

            # Step 2: Calculate scores
            scores = await self._calculate_scores(features)

            # Step 3: Determine rank
            rank = self._determine_rank(scores.overall)

            # Step 4: Generate analysis
            analysis = await self._generate_analysis(
                enterprise_name or credit_code, scores, rank, include_details
            )

            # Step 5: Format radar data
            radar_data = self._format_radar_data(scores)

            return KechuangEvaluatorOutput(
                success=True,
                scores=scores,
                radar_data=radar_data,
                analysis=analysis,
                rank=rank,
                enterprise_name=enterprise_name or f"企业({credit_code[:8]}...)",
                data={
                    "features": features,
                    "include_details": include_details,
                },
            )

        except Exception as e:
            logger.error(f"Kechuang evaluation failed: {e}")
            return KechuangEvaluatorOutput(
                success=False,
                error=str(e),
            )

    async def _get_enterprise_features(
        self, enterprise_name: str, credit_code: str
    ) -> dict[str, Any]:
        """Get enterprise features from data warehouse.

        Note: This is mock implementation. In production, call actual services.
        """
        # TODO: Integrate with data_warehouse adapter
        service_config = self.get_service_config("data_warehouse")
        if service_config:
            logger.info(f"Would call endpoint: {service_config.endpoint}")

        # Mock features for demonstration
        return {
            "patent_count": random.randint(5, 50),
            "rd_investment_ratio": round(random.uniform(0.05, 0.20), 2),
            "tech_team_size": random.randint(10, 100),
            "revenue_growth": round(random.uniform(0.10, 0.50), 2),
            "employee_growth": round(random.uniform(0.05, 0.30), 2),
            "years_in_operation": random.randint(3, 15),
            "financial_score": round(random.uniform(60, 95), 1),
            "partnerships": random.randint(2, 10),
            "government_grants": random.randint(0, 5),
        }

    async def _calculate_scores(self, features: dict[str, Any]) -> ScoreBreakdown:
        """Calculate scores based on features.

        Note: This is mock implementation. In production, call model factory.
        """
        # TODO: Integrate with model_factory adapter
        service_config = self.get_service_config("model_factory")
        if service_config:
            logger.info(f"Would call model: {service_config.model}")

        # Mock score calculation
        innovation = min(100, 40 + features["patent_count"] * 1.2
                        + features["rd_investment_ratio"] * 100
                        + features["tech_team_size"] * 0.2)

        growth = min(100, 30 + features["revenue_growth"] * 100
                    + features["employee_growth"] * 80)

        stability = min(100, 50 + features["years_in_operation"] * 2
                       + features["financial_score"] * 0.4)

        cooperation = min(100, 40 + features["partnerships"] * 5
                         + features["government_grants"] * 8)

        # Calculate weighted overall
        overall = (
            innovation * self.WEIGHTS["innovation"]
            + growth * self.WEIGHTS["growth"]
            + stability * self.WEIGHTS["stability"]
            + cooperation * self.WEIGHTS["cooperation"]
        )

        return ScoreBreakdown(
            innovation=round(innovation, 1),
            growth=round(growth, 1),
            stability=round(stability, 1),
            cooperation=round(cooperation, 1),
            overall=round(overall, 1),
        )

    def _determine_rank(self, overall_score: float) -> str:
        """Determine rank based on overall score."""
        if overall_score >= 85:
            return "A"
        elif overall_score >= 70:
            return "B"
        elif overall_score >= 55:
            return "C"
        else:
            return "D"

    async def _generate_analysis(
        self,
        enterprise_name: str,
        scores: ScoreBreakdown,
        rank: str,
        include_details: bool,
    ) -> str:
        """Generate analysis text.

        Note: This is simplified. In production, use LLM for natural language.
        """
        # Find strengths and weaknesses
        score_dict = {
            "创新力": scores.innovation,
            "成长性": scores.growth,
            "稳定性": scores.stability,
            "合作度": scores.cooperation,
        }
        
        strengths = [k for k, v in score_dict.items() if v >= 80]
        weaknesses = [k for k, v in score_dict.items() if v < 60]

        analysis = f"{enterprise_name} 综合评级为 {rank} 级，综合得分 {scores.overall}。"

        if include_details:
            if strengths:
                analysis += f"优势领域：{', '.join(strengths)}。"
            if weaknesses:
                analysis += f"待提升领域：{', '.join(weaknesses)}。"

        return analysis

    def _format_radar_data(self, scores: ScoreBreakdown) -> list[RadarDataPoint]:
        """Format scores as radar chart data."""
        return [
            RadarDataPoint(axis="创新力", value=scores.innovation),
            RadarDataPoint(axis="成长性", value=scores.growth),
            RadarDataPoint(axis="稳定性", value=scores.stability),
            RadarDataPoint(axis="合作度", value=scores.cooperation),
            RadarDataPoint(axis="综合", value=scores.overall),
        ]

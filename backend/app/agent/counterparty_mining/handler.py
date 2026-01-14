"""
Counterparty Mining Handler

交易对手挖掘 Agent 业务逻辑实现
"""

import logging
import random
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.agent.base import AgentInput, AgentOutput, BaseAgent
from app.agent.registry import register_agent

logger = logging.getLogger(__name__)


class CounterpartyMiningInput(AgentInput):
    """Counterparty mining input schema."""

    enterprise_name: str = Field(default="", description="目标企业名称")
    credit_code: str = Field(default="", description="统一社会信用代码")
    direction: Literal["upstream", "downstream", "both"] = Field(
        default="both", description="挖掘方向"
    )
    depth: int = Field(default=2, ge=1, le=3, description="挖掘深度")
    limit: int = Field(default=20, ge=1, le=100, description="结果限制")


class CounterpartyInfo(BaseModel):
    """Counterparty information."""

    name: str = Field(..., description="企业名称")
    credit_code: str = Field(default="", description="统一社会信用代码")
    relation_type: str = Field(..., description="关系类型: upstream/downstream")
    relation_desc: str = Field(default="", description="关系描述")
    strength: float = Field(default=0.5, ge=0, le=1, description="关系强度")
    depth: int = Field(default=1, description="关系层级")


class GraphNode(BaseModel):
    """Graph node for visualization."""

    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    type: str = Field(default="enterprise", description="节点类型")
    is_target: bool = Field(default=False, description="是否为目标企业")


class GraphEdge(BaseModel):
    """Graph edge for visualization."""

    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    relation: str = Field(..., description="关系类型")
    weight: float = Field(default=1.0, description="边权重")


class GraphData(BaseModel):
    """Graph data for RelationGraph component."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class Statistics(BaseModel):
    """Mining statistics."""

    upstream_count: int = Field(default=0)
    downstream_count: int = Field(default=0)
    total_count: int = Field(default=0)
    max_depth: int = Field(default=0)


class CounterpartyMiningOutput(AgentOutput):
    """Counterparty mining output schema."""

    counterparties: list[CounterpartyInfo] = Field(
        default_factory=list, description="交易对手列表"
    )
    graph_data: GraphData | None = Field(default=None, description="关系图谱数据")
    statistics: Statistics | None = Field(default=None, description="统计信息")
    target_enterprise: str = Field(default="", description="目标企业名称")


@register_agent
class CounterpartyMiningAgent(BaseAgent):
    """交易对手挖掘 Agent.

    基于目标企业挖掘上下游交易对手：
    - 上游供应商挖掘
    - 下游客户挖掘
    - 关系图谱生成
    """

    name = "counterparty_mining"
    description = "交易对手挖掘 Agent - 挖掘企业上下游交易对手"
    version = "1.0.0"

    # Mock enterprise data for demonstration
    MOCK_ENTERPRISES = [
        ("华强供应链有限公司", "91440300MA5...", "供应商", "原材料供应"),
        ("中科创新科技", "91110000MA0...", "供应商", "技术服务"),
        ("恒达物流集团", "91310000MA1...", "供应商", "物流服务"),
        ("新华贸易有限公司", "91320500MA2...", "客户", "产品销售"),
        ("博雅软件科技", "91440100MA3...", "客户", "软件服务"),
        ("长城电子集团", "91110108MA4...", "客户", "设备采购"),
        ("鼎盛投资有限公司", "91330100MA5...", "客户", "投资合作"),
        ("远东材料科技", "91210200MA6...", "供应商", "原材料"),
    ]

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute counterparty mining logic.

        Args:
            input_data: Input containing target enterprise info

        Returns:
            Output containing counterparties and graph data
        """
        # Parse input
        if isinstance(input_data, CounterpartyMiningInput):
            enterprise_name = input_data.enterprise_name
            credit_code = input_data.credit_code
            direction = input_data.direction
            depth = input_data.depth
            limit = input_data.limit
        else:
            enterprise_name = getattr(input_data, "enterprise_name", "")
            credit_code = getattr(input_data, "credit_code", "")
            direction = getattr(input_data, "direction", "both")
            depth = getattr(input_data, "depth", 2)
            limit = getattr(input_data, "limit", 20)

        # Validate input
        if not enterprise_name and not credit_code:
            return CounterpartyMiningOutput(
                success=False,
                error="必须提供企业名称或统一社会信用代码",
            )

        try:
            target_name = enterprise_name or f"企业({credit_code[:8]}...)"

            # Step 1: Mine counterparties
            counterparties = await self._mine_counterparties(
                enterprise_name, credit_code, direction, depth, limit
            )

            # Step 2: Build graph data
            graph_data = self._build_graph_data(target_name, counterparties)

            # Step 3: Calculate statistics
            statistics = self._calculate_statistics(counterparties, depth)

            return CounterpartyMiningOutput(
                success=True,
                counterparties=counterparties,
                graph_data=graph_data,
                statistics=statistics,
                target_enterprise=target_name,
                data={
                    "direction": direction,
                    "depth": depth,
                    "limit": limit,
                },
            )

        except Exception as e:
            logger.error(f"Counterparty mining failed: {e}")
            return CounterpartyMiningOutput(
                success=False,
                error=str(e),
            )

    async def _mine_counterparties(
        self,
        enterprise_name: str,
        credit_code: str,
        direction: str,
        depth: int,
        limit: int,
    ) -> list[CounterpartyInfo]:
        """Mine counterparties from data sources.

        Note: This is mock implementation. In production, call actual services.
        """
        # TODO: Integrate with data_warehouse adapter
        service_config = self.get_service_config("data_warehouse")
        if service_config:
            logger.info(f"Would call endpoint: {service_config.endpoint}")

        results: list[CounterpartyInfo] = []

        for name, code, role, desc in self.MOCK_ENTERPRISES:
            # Filter by direction
            if direction == "upstream" and role != "供应商":
                continue
            if direction == "downstream" and role != "客户":
                continue

            rel_type = "upstream" if role == "供应商" else "downstream"
            rel_depth = random.randint(1, depth)

            results.append(
                CounterpartyInfo(
                    name=name,
                    credit_code=code,
                    relation_type=rel_type,
                    relation_desc=desc,
                    strength=round(random.uniform(0.3, 0.95), 2),
                    depth=rel_depth,
                )
            )

            if len(results) >= limit:
                break

        # Sort by strength
        results.sort(key=lambda x: x.strength, reverse=True)
        return results

    def _build_graph_data(
        self, target_name: str, counterparties: list[CounterpartyInfo]
    ) -> GraphData:
        """Build graph data for visualization."""
        nodes: list[GraphNode] = [
            GraphNode(id="target", name=target_name, type="target", is_target=True)
        ]
        edges: list[GraphEdge] = []

        for idx, cp in enumerate(counterparties):
            node_id = f"cp_{idx}"
            nodes.append(
                GraphNode(
                    id=node_id,
                    name=cp.name,
                    type=cp.relation_type,
                )
            )

            # Edge direction based on relation type
            if cp.relation_type == "upstream":
                edges.append(
                    GraphEdge(
                        source=node_id,
                        target="target",
                        relation="供应",
                        weight=cp.strength,
                    )
                )
            else:
                edges.append(
                    GraphEdge(
                        source="target",
                        target=node_id,
                        relation="销售",
                        weight=cp.strength,
                    )
                )

        return GraphData(nodes=nodes, edges=edges)

    def _calculate_statistics(
        self, counterparties: list[CounterpartyInfo], depth: int
    ) -> Statistics:
        """Calculate mining statistics."""
        upstream = sum(1 for cp in counterparties if cp.relation_type == "upstream")
        downstream = sum(1 for cp in counterparties if cp.relation_type == "downstream")

        return Statistics(
            upstream_count=upstream,
            downstream_count=downstream,
            total_count=len(counterparties),
            max_depth=depth,
        )

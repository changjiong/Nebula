"""
Tests for the Planner Layer - Intent Understanding and Agent Routing

Tests cover:
- IntentType enum values
- Intent and ExtractedParams dataclasses
- RuleBasedClassifier keyword matching
- BasicParameterExtractor pattern extraction
- AgentRouter routing logic
- Planner orchestration
"""

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from app.engine.planner import (
    IntentType,
    Intent,
    ExtractedParams,
    RoutingDecision,
    RuleBasedClassifier,
    BasicParameterExtractor,
    AgentRouter,
    Planner,
)


# ============================================================================
# Intent and ExtractedParams Tests
# ============================================================================

class TestIntentType:
    def test_enum_values(self):
        """Verify all intent types are defined."""
        assert IntentType.QUERY.value == "query"
        assert IntentType.ANALYSIS.value == "analysis"
        assert IntentType.PREDICTION.value == "prediction"
        assert IntentType.WORKFLOW.value == "workflow"
        assert IntentType.CONVERSATION.value == "conversation"
        assert IntentType.UNKNOWN.value == "unknown"


class TestIntent:
    def test_intent_creation(self):
        """Test Intent dataclass creation."""
        intent = Intent(
            type=IntentType.QUERY,
            confidence=0.9,
            sub_type="enterprise",
            description="Enterprise query detected",
            metadata={"key": "value"}
        )
        
        assert intent.type == IntentType.QUERY
        assert intent.confidence == 0.9
        assert intent.sub_type == "enterprise"
        assert intent.description == "Enterprise query detected"
        assert intent.metadata == {"key": "value"}
    
    def test_intent_defaults(self):
        """Test Intent default values."""
        intent = Intent(type=IntentType.QUERY, confidence=0.8)
        
        assert intent.sub_type is None
        assert intent.description is None
        assert intent.metadata == {}


class TestExtractedParams:
    def test_get_from_entities(self):
        """Test parameter retrieval from entities."""
        params = ExtractedParams(
            entities={"company": "Acme Corp"},
            filters={},
            options={}
        )
        
        assert params.get("company") == "Acme Corp"
        assert params.get("missing", "default") == "default"
    
    def test_get_priority_order(self):
        """Test that entities take priority over filters and options."""
        params = ExtractedParams(
            entities={"key": "entity_value"},
            filters={"key": "filter_value"},
            options={"key": "option_value"}
        )
        
        # Entities should be checked first
        assert params.get("key") == "entity_value"
    
    def test_to_dict(self):
        """Test conversion to flat dictionary."""
        params = ExtractedParams(
            entities={"company": "Acme"},
            filters={"time": "today"},
            options={"limit": 10},
            raw_text="show me Acme"
        )
        
        result = params.to_dict()
        assert result["company"] == "Acme"
        assert result["time"] == "today"
        assert result["limit"] == 10
        assert result["_raw_text"] == "show me Acme"


# ============================================================================
# RuleBasedClassifier Tests
# ============================================================================

class TestRuleBasedClassifier:
    @pytest.fixture
    def classifier(self):
        return RuleBasedClassifier()
    
    @pytest.mark.anyio
    async def test_query_intent_chinese(self, classifier):
        """Test Chinese query keyword detection."""
        intent = await classifier.classify("查询某企业的信息")
        assert intent.type == IntentType.QUERY
        assert intent.confidence == 0.8
    
    @pytest.mark.anyio
    async def test_query_intent_english(self, classifier):
        """Test English query keyword detection."""
        intent = await classifier.classify("find companies in Beijing")
        assert intent.type == IntentType.QUERY
    
    @pytest.mark.anyio
    async def test_analysis_intent(self, classifier):
        """Test analysis intent detection."""
        intent = await classifier.classify("分析这个企业的趋势")
        assert intent.type == IntentType.ANALYSIS
    
    @pytest.mark.anyio
    async def test_prediction_intent(self, classifier):
        """Test prediction intent detection."""
        intent = await classifier.classify("评估风险评分")
        assert intent.type == IntentType.PREDICTION
    
    @pytest.mark.anyio
    async def test_workflow_intent(self, classifier):
        """Test workflow intent detection."""
        intent = await classifier.classify("提交审批流程")
        assert intent.type == IntentType.WORKFLOW
    
    @pytest.mark.anyio
    async def test_conversation_fallback(self, classifier):
        """Test that unmatched input falls back to conversation."""
        intent = await classifier.classify("你好，今天天气怎么样")
        assert intent.type == IntentType.CONVERSATION
        assert intent.confidence == 0.5
    
    @pytest.mark.anyio
    async def test_case_insensitive(self, classifier):
        """Test that keyword matching is case insensitive."""
        intent = await classifier.classify("SEARCH for companies")
        assert intent.type == IntentType.QUERY


# ============================================================================
# BasicParameterExtractor Tests
# ============================================================================

class TestBasicParameterExtractor:
    @pytest.fixture
    def extractor(self):
        return BasicParameterExtractor()
    
    @pytest.fixture
    def query_intent(self):
        return Intent(type=IntentType.QUERY, confidence=0.8)
    
    @pytest.mark.anyio
    async def test_extract_time_range_chinese(self, extractor, query_intent):
        """Test Chinese time range extraction."""
        params = await extractor.extract("查询今天的数据", query_intent)
        assert params.filters.get("time_range") == "今天"
    
    @pytest.mark.anyio
    async def test_extract_time_range_english(self, extractor, query_intent):
        """Test English time range extraction."""
        params = await extractor.extract("show data from yesterday", query_intent)
        assert params.filters.get("time_range") == "yesterday"
    
    @pytest.mark.anyio
    async def test_extract_limit_chinese(self, extractor, query_intent):
        """Test Chinese limit extraction."""
        params = await extractor.extract("显示前10个企业", query_intent)
        assert params.options.get("limit") == 10
    
    @pytest.mark.anyio
    async def test_extract_limit_english(self, extractor, query_intent):
        """Test English limit extraction."""
        params = await extractor.extract("show top 5 companies", query_intent)
        assert params.options.get("limit") == 5
    
    @pytest.mark.anyio
    async def test_preserve_raw_text(self, extractor, query_intent):
        """Test that raw text is preserved."""
        message = "查询企业信息"
        params = await extractor.extract(message, query_intent)
        assert params.raw_text == message


# ============================================================================
# AgentRouter Tests
# ============================================================================

class TestAgentRouter:
    @pytest.fixture
    def router(self):
        return AgentRouter()
    
    def test_route_query_intent(self, router):
        """Test routing for query intent."""
        intent = Intent(type=IntentType.QUERY, confidence=0.8)
        params = ExtractedParams()
        
        decision = router.route(intent, params)
        
        assert decision.target_agent == "data_query_agent"
        assert "analytics_agent" in decision.fallback_agents
    
    def test_route_analysis_intent(self, router):
        """Test routing for analysis intent."""
        intent = Intent(type=IntentType.ANALYSIS, confidence=0.8)
        params = ExtractedParams()
        
        decision = router.route(intent, params)
        
        assert decision.target_agent == "analytics_agent"
    
    def test_route_prediction_intent(self, router):
        """Test routing for prediction intent."""
        intent = Intent(type=IntentType.PREDICTION, confidence=0.8)
        params = ExtractedParams()
        
        decision = router.route(intent, params)
        
        assert decision.target_agent == "prediction_agent"
    
    def test_route_workflow_intent(self, router):
        """Test routing for workflow intent with highest priority."""
        intent = Intent(type=IntentType.WORKFLOW, confidence=0.8)
        params = ExtractedParams()
        
        decision = router.route(intent, params)
        
        assert decision.target_agent == "workflow_agent"
        assert decision.priority == 10  # Highest priority
    
    def test_route_conversation_default(self, router):
        """Test that conversation routes to chat agent."""
        intent = Intent(type=IntentType.CONVERSATION, confidence=0.5)
        params = ExtractedParams()
        
        decision = router.route(intent, params)
        
        assert decision.target_agent == "chat_agent"
    
    def test_register_custom_agent(self, router):
        """Test registering a custom agent."""
        router.register_agent(
            IntentType.QUERY,
            "custom_query_agent",
            fallbacks=["backup_agent"]
        )
        
        intent = Intent(type=IntentType.QUERY, confidence=0.8)
        decision = router.route(intent, ExtractedParams())
        
        assert decision.target_agent == "custom_query_agent"
        assert "backup_agent" in decision.fallback_agents


# ============================================================================
# Planner Integration Tests
# ============================================================================

class TestPlanner:
    @pytest.fixture
    def planner(self):
        return Planner()
    
    @pytest.mark.anyio
    async def test_plan_query(self, planner):
        """Test full planning pipeline for query."""
        decision = await planner.plan("查询企业信息")
        
        assert isinstance(decision, RoutingDecision)
        assert decision.intent.type == IntentType.QUERY
        assert decision.target_agent == "data_query_agent"
    
    @pytest.mark.anyio
    async def test_planner_langraph_interface(self, planner):
        """Test LangGraph node interface."""
        state = {
            "input": "分析趋势",
            "messages": [],
        }
        
        result = await planner(state)
        
        assert "intent" in result
        assert result["intent"] == "analysis"
        assert "intent_confidence" in result
        assert "target_agent" in result
        assert "extracted_params" in result
        assert "fallback_agents" in result
    
    @pytest.mark.anyio
    async def test_planner_with_context(self, planner):
        """Test planning with conversation context."""
        context = [
            HumanMessage(content="我想了解企业信息"),
            AIMessage(content="好的，请告诉我企业名称"),
        ]
        
        decision = await planner.plan("先进数通", context)
        
        # Should still process the message
        assert isinstance(decision, RoutingDecision)

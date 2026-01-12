"""
Model Factory Adapter Module

Provides adapter for connecting to enterprise Model Factory (模型工厂) APIs.
"""

import logging
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.adapters.base import (
    AdapterConfig,
    AdapterError,
    AdapterRequest,
    HTTPAdapter,
)

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Types of ML models"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"
    NLP = "nlp"


class ModelStatus(str, Enum):
    """Model deployment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PredictionStatus(str, Enum):
    """Prediction request status"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class ModelInfo(BaseModel):
    """Model metadata information"""
    model_id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Model name")
    version: str = Field(default="1.0.0")
    model_type: ModelType
    status: ModelStatus = Field(default=ModelStatus.ACTIVE)
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class PredictionRequest(BaseModel):
    """Prediction request"""
    model_id: str
    inputs: list[dict[str, Any]]
    model_version: str | None = None
    batch_mode: bool = False
    timeout: int | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class PredictionResult(BaseModel):
    """Prediction result"""
    prediction_id: str
    model_id: str
    model_version: str
    status: PredictionStatus
    predictions: list[dict[str, Any]] = Field(default_factory=list)
    confidence_scores: list[float] | None = None
    execution_time_ms: float = 0
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelFactoryConfig(AdapterConfig):
    """Model Factory specific configuration"""
    default_timeout: int = 60
    max_batch_size: int = 1000


# Mock Models
MOCK_MODELS = [
    ModelInfo(
        model_id="credit-score-v2",
        name="信用评分模型",
        version="2.1.0",
        model_type=ModelType.CLASSIFICATION,
        description="基于多维特征的企业信用评分模型",
        metrics={"accuracy": 0.92, "auc": 0.95},
        tags=["credit", "risk"],
    ),
    ModelInfo(
        model_id="fraud-detection-v1",
        name="欺诈检测模型",
        version="1.5.0",
        model_type=ModelType.ANOMALY_DETECTION,
        description="实时交易欺诈检测模型",
        metrics={"precision": 0.95, "recall": 0.88},
        tags=["fraud", "detection"],
    ),
    ModelInfo(
        model_id="loan-approval-v3",
        name="贷款审批模型",
        version="3.0.0",
        model_type=ModelType.CLASSIFICATION,
        description="贷款审批决策模型",
        metrics={"accuracy": 0.88},
        tags=["loan", "approval"],
    ),
]


def _generate_mock_predictions(
    model_id: str, inputs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Generate mock predictions based on model type"""
    import random
    predictions = []
    for i, _ in enumerate(inputs):
        if model_id == "credit-score-v2":
            score = random.randint(500, 900)
            rating = "AAA" if score >= 800 else "AA" if score >= 700 else "A"
            predictions.append({"score": score, "rating": rating})
        elif model_id == "fraud-detection-v1":
            prob = random.uniform(0.01, 0.15)
            predictions.append({"is_fraud": prob > 0.1, "fraud_probability": round(prob, 4)})
        elif model_id == "loan-approval-v3":
            approved = random.random() > 0.35
            predictions.append({"approved": approved, "max_amount": random.randint(10000, 500000) if approved else 0})
        else:
            predictions.append({"prediction": f"mock_result_{i}", "confidence": 0.85})
    return predictions


class ModelFactoryAdapter(HTTPAdapter):
    """
    Model Factory API Adapter (模型工厂适配器)

    Usage:
        adapter = ModelFactoryAdapter(ModelFactoryConfig(mock_mode=True))
        result = adapter.predict(PredictionRequest(
            model_id="credit-score-v2",
            inputs=[{"company_id": "C001", "revenue": 1000000}]
        ))
    """

    def __init__(self, config: ModelFactoryConfig | None = None):
        super().__init__(config or ModelFactoryConfig())
        self._mf_config: ModelFactoryConfig = self.config  # type: ignore

    def _mock_predict(self, request: PredictionRequest) -> PredictionResult:
        """Generate mock prediction result"""
        predictions = _generate_mock_predictions(request.model_id, request.inputs)
        return PredictionResult(
            prediction_id=f"pred-{uuid4().hex[:12]}",
            model_id=request.model_id,
            model_version=request.model_version or "1.0.0",
            status=PredictionStatus.SUCCESS,
            predictions=predictions,
            confidence_scores=[0.85 + (i * 0.01) for i in range(len(predictions))],
            execution_time_ms=50.0,
            metadata={"mock": True},
        )

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make prediction using specified model."""
        if self.config.mock_mode:
            logger.info(f"[ModelFactory] Mock prediction: {request.model_id}")
            return self._mock_predict(request)

        adapter_request = AdapterRequest(
            endpoint=f"/api/v1/models/{request.model_id}/predict",
            method="POST",
            body={"inputs": request.inputs, "model_version": request.model_version},
            timeout=request.timeout or self._mf_config.default_timeout,
        )
        response = self.call(adapter_request)
        if response.error:
            return PredictionResult(
                prediction_id=f"pred-{uuid4().hex[:12]}",
                model_id=request.model_id,
                model_version="unknown",
                status=PredictionStatus.FAILED,
                error_message=response.error,
            )
        return PredictionResult(**response.data) if response.data else PredictionResult(
            prediction_id=f"pred-{uuid4().hex[:12]}",
            model_id=request.model_id,
            model_version="unknown",
            status=PredictionStatus.FAILED,
            error_message="Empty response",
        )

    async def async_predict(self, request: PredictionRequest) -> PredictionResult:
        """Async version of predict"""
        if self.config.mock_mode:
            return self._mock_predict(request)
        adapter_request = AdapterRequest(
            endpoint=f"/api/v1/models/{request.model_id}/predict",
            method="POST",
            body={"inputs": request.inputs, "model_version": request.model_version},
        )
        response = await self.async_call(adapter_request)
        if response.error:
            return PredictionResult(
                prediction_id=f"pred-{uuid4().hex[:12]}",
                model_id=request.model_id,
                model_version="unknown",
                status=PredictionStatus.FAILED,
                error_message=response.error,
            )
        return PredictionResult(**response.data) if response.data else PredictionResult(
            prediction_id=f"pred-{uuid4().hex[:12]}",
            model_id=request.model_id,
            model_version="unknown",
            status=PredictionStatus.FAILED,
        )

    def list_models(self, model_type: ModelType | None = None) -> list[ModelInfo]:
        """List available models."""
        if self.config.mock_mode:
            models = MOCK_MODELS.copy()
            if model_type:
                models = [m for m in models if m.model_type == model_type]
            return models
        response = self.call(AdapterRequest(endpoint="/api/v1/models", method="GET"))
        if response.error:
            raise AdapterError(f"Failed to list models: {response.error}")
        return [ModelInfo(**m) for m in (response.data or [])]

    async def async_list_models(self, model_type: ModelType | None = None) -> list[ModelInfo]:
        """Async version of list_models"""
        if self.config.mock_mode:
            models = MOCK_MODELS.copy()
            if model_type:
                models = [m for m in models if m.model_type == model_type]
            return models
        response = await self.async_call(AdapterRequest(endpoint="/api/v1/models", method="GET"))
        if response.error:
            raise AdapterError(f"Failed to list models: {response.error}")
        return [ModelInfo(**m) for m in (response.data or [])]

    def get_model(self, model_id: str) -> ModelInfo | None:
        """Get model details by ID."""
        if self.config.mock_mode:
            for model in MOCK_MODELS:
                if model.model_id == model_id:
                    return model
            return None
        response = self.call(AdapterRequest(endpoint=f"/api/v1/models/{model_id}", method="GET"))
        return ModelInfo(**response.data) if response.data else None

    def health_check(self) -> dict[str, Any]:
        """Check Model Factory service health."""
        if self.config.mock_mode:
            return {"status": "healthy", "active_models": len(MOCK_MODELS), "mock_mode": True}
        response = self.call(AdapterRequest(endpoint="/api/v1/health", method="GET"))
        return {"status": "healthy" if not response.error else "unhealthy", "latency_ms": response.latency_ms}

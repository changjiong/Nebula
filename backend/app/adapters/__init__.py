"""
Adapters Module

External service adapters for:
- Data Warehouse (数仓)
- Model Factory (模型工厂)
- External APIs (外部数据接口)

All adapters provide:
- Unified request/response format
- Synchronous and asynchronous call support
- Timeout handling and error retry
- Mock mode for testing
"""

from app.adapters.base import (
    AdapterConfig,
    AdapterConnectionError,
    AdapterError,
    AdapterRequest,
    AdapterResponse,
    AdapterRetryExhaustedError,
    AdapterStatus,
    AdapterTimeoutError,
    BaseAdapter,
    HTTPAdapter,
    RetryStrategy,
)
from app.adapters.data_warehouse import (
    DataFormat,
    DataWarehouseAdapter,
    DataWarehouseConfig,
    QueryRequest,
    QueryResult,
    QueryStatus,
    QueryType,
    TableInfo,
)
from app.adapters.external_api import (
    CompanyInfo,
    CourtRecord,
    CreditReport,
    DataSource,
    ExternalAPIAdapter,
    ExternalAPIConfig,
)
from app.adapters.model_factory import (
    ModelFactoryAdapter,
    ModelFactoryConfig,
    ModelInfo,
    ModelStatus,
    ModelType,
    PredictionRequest,
    PredictionResult,
    PredictionStatus,
)

__all__ = [
    # Base
    "AdapterConfig",
    "AdapterError",
    "AdapterRequest",
    "AdapterResponse",
    "AdapterStatus",
    "AdapterTimeoutError",
    "AdapterConnectionError",
    "AdapterRetryExhaustedError",
    "BaseAdapter",
    "HTTPAdapter",
    "RetryStrategy",
    # Data Warehouse
    "DataWarehouseAdapter",
    "DataWarehouseConfig",
    "QueryRequest",
    "QueryResult",
    "QueryStatus",
    "QueryType",
    "DataFormat",
    "TableInfo",
    # Model Factory
    "ModelFactoryAdapter",
    "ModelFactoryConfig",
    "ModelInfo",
    "ModelStatus",
    "ModelType",
    "PredictionRequest",
    "PredictionResult",
    "PredictionStatus",
    # External API
    "ExternalAPIAdapter",
    "ExternalAPIConfig",
    "CompanyInfo",
    "CreditReport",
    "CourtRecord",
    "DataSource",
]

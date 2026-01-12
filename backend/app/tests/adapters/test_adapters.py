from unittest.mock import MagicMock, patch

import pytest

from app.adapters.base import (
    AdapterConfig,
    AdapterRequest,
    AdapterStatus,
    HTTPAdapter,
)
from app.adapters.data_warehouse import (
    DataWarehouseAdapter,
    DataWarehouseConfig,
    QueryRequest,
    QueryStatus,
)
from app.adapters.external_api import (
    ExternalAPIAdapter,
    ExternalAPIConfig,
)
from app.adapters.model_factory import (
    ModelFactoryAdapter,
    ModelFactoryConfig,
    ModelType,
    PredictionRequest,
    PredictionStatus,
)

# ============================================================================
# Base Adapter Tests
# ============================================================================

class TestBaseAdapter:
    def test_initialization(self):
        config = AdapterConfig(base_url="http://test.com", timeout=10.0)
        adapter = HTTPAdapter(config)
        assert adapter.config.base_url == "http://test.com"
        assert adapter.config.timeout == 10.0

    def test_mock_mode(self):
        config = AdapterConfig(mock_mode=True)
        adapter = HTTPAdapter(config)
        adapter.set_mock_response("/test", {"foo": "bar"})

        request = AdapterRequest(endpoint="/test", method="GET")
        response = adapter.call(request)

        assert response.status == AdapterStatus.MOCK
        assert response.data == {"foo": "bar"}
        assert response.metadata.get("mock") is True

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_async_mock_mode(self):
        config = AdapterConfig(mock_mode=True)
        adapter = HTTPAdapter(config)
        adapter.set_mock_response("/test", {"foo": "bar"})

        request = AdapterRequest(endpoint="/test", method="GET")
        response = await adapter.async_call(request)

        assert response.status == AdapterStatus.MOCK
        assert response.data == {"foo": "bar"}

# ============================================================================
# Data Warehouse Adapter Tests
# ============================================================================

class TestDataWarehouseAdapter:
    def test_mock_query_execution(self):
        config = DataWarehouseConfig(mock_mode=True)
        adapter = DataWarehouseAdapter(config)

        request = QueryRequest(query="SELECT * FROM customers")
        result = adapter.execute_query(request)

        assert result.status == QueryStatus.COMPLETED
        assert len(result.data) > 0
        assert "mock" in result.metadata

    def test_mock_list_tables(self):
        config = DataWarehouseConfig(mock_mode=True)
        adapter = DataWarehouseAdapter(config)

        tables = adapter.list_tables()
        assert len(tables) > 0
        assert tables[0].table_name == "customers"

    @patch("app.adapters.base.httpx.Client")
    def test_real_query_execution(self, mock_client_cls):
        # Mocking the underlying HTTP client response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "data": [{"col1": "val1"}],
            "query_id": "test-query",
            "rows_affected": 1,
            "columns": ["col1"]
        }
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value = mock_client

        config = DataWarehouseConfig(base_url="http://dw.test")
        adapter = DataWarehouseAdapter(config)

        request = QueryRequest(query="SELECT 1")
        result = adapter.execute_query(request)

        assert result.status == QueryStatus.COMPLETED
        assert result.data == [{"col1": "val1"}]

        # Verify call arguments
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["json"]["query"] == "SELECT 1"

# ============================================================================
# Model Factory Adapter Tests
# ============================================================================

class TestModelFactoryAdapter:
    def test_mock_prediction(self):
        config = ModelFactoryConfig(mock_mode=True)
        adapter = ModelFactoryAdapter(config)

        request = PredictionRequest(
            model_id="credit-score-v2",
            inputs=[{"id": "123"}]
        )
        result = adapter.predict(request)

        assert result.status == PredictionStatus.SUCCESS
        assert len(result.predictions) == 1
        assert "score" in result.predictions[0]

    def test_mock_list_models(self):
        config = ModelFactoryConfig(mock_mode=True)
        adapter = ModelFactoryAdapter(config)

        models = adapter.list_models(model_type=ModelType.CLASSIFICATION)
        assert len(models) > 0
        assert models[0].model_type == ModelType.CLASSIFICATION

# ============================================================================
# External API Adapter Tests
# ============================================================================

class TestExternalAPIAdapter:
    def test_mock_company_info(self):
        config = ExternalAPIConfig(mock_mode=True)
        adapter = ExternalAPIAdapter(config)

        company = adapter.get_company_info("91110000100000001A")
        assert company is not None
        assert company.name == "北京示例科技有限公司"

        # Test non-existent company
        company = adapter.get_company_info("NON_EXISTENT")
        assert company is None

    def test_mock_credit_report(self):
        config = ExternalAPIConfig(mock_mode=True)
        adapter = ExternalAPIAdapter(config)

        report = adapter.get_credit_report("91110000100000001A")
        assert report is not None
        assert report.credit_score == 780

# Adapters Module

External service adapters for data warehouse, model factory, and external APIs.

## Features

- **Unified Interface**: All adapters share the same `call()` and `async_call()` methods
- **Request/Response Format**: Standardized `AdapterRequest` and `AdapterResponse` models
- **Timeout Handling**: Configurable timeout with automatic error handling
- **Error Retry**: Exponential backoff retry with configurable attempts
- **Mock Mode**: Built-in mock responses for testing without external dependencies

## Files

- `base.py` - Base adapter class with unified interface
- `data_warehouse.py` - Data warehouse API adapter (数仓)
- `model_factory.py` - Model factory adapter (模型工厂)
- `external_api.py` - External API adapter (e.g., business registration 工商数据)

## Quick Start

### Data Warehouse Adapter

```python
from app.adapters import DataWarehouseAdapter, DataWarehouseConfig, QueryRequest

# Create adapter (mock mode for testing)
config = DataWarehouseConfig(
    base_url="http://datawarehouse.internal:8080",
    database="analytics",
    mock_mode=True
)
adapter = DataWarehouseAdapter(config)

# Execute query
result = adapter.execute_query(QueryRequest(
    query="SELECT * FROM customers LIMIT 10"
))
print(result.data)

# List tables
tables = adapter.list_tables()
```

### Model Factory Adapter

```python
from app.adapters import ModelFactoryAdapter, ModelFactoryConfig, PredictionRequest

# Create adapter
config = ModelFactoryConfig(mock_mode=True)
adapter = ModelFactoryAdapter(config)

# List available models
models = adapter.list_models()

# Make prediction
result = adapter.predict(PredictionRequest(
    model_id="credit-score-v2",
    inputs=[{"company_id": "C001", "revenue": 1000000}]
))
print(result.predictions)
```

### External API Adapter

```python
from app.adapters import ExternalAPIAdapter, ExternalAPIConfig

# Create adapter
config = ExternalAPIConfig(
    base_url="https://api.external.com",
    api_key="your-api-key",
    mock_mode=True
)
adapter = ExternalAPIAdapter(config)

# Get company info (工商数据)
company = adapter.get_company_info("91110000100000001A")

# Get credit report (征信报告)
credit = adapter.get_credit_report("91110000100000001A")
```

### Async Usage

All adapters support async operations:

```python
import asyncio
from app.adapters import DataWarehouseAdapter, DataWarehouseConfig, QueryRequest

async def main():
    adapter = DataWarehouseAdapter(DataWarehouseConfig(mock_mode=True))
    result = await adapter.async_execute_query(QueryRequest(
        query="SELECT * FROM transactions"
    ))
    print(result.data)
    await adapter.aclose()

asyncio.run(main())
```

## Configuration

### Base Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | str | "" | Base URL for API calls |
| `timeout` | float | 30.0 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `retry_strategy` | RetryStrategy | EXPONENTIAL | Retry strategy |
| `mock_mode` | bool | False | Enable mock responses |
| `auth_token` | str | None | Bearer token for auth |

### Mock Mode

All adapters support mock mode for testing:

```python
adapter = DataWarehouseAdapter(DataWarehouseConfig(mock_mode=True))

# Set custom mock response
adapter.set_mock_response("/custom/endpoint", {"custom": "data"})

# Clear all mock responses
adapter.clear_mock_responses()
```

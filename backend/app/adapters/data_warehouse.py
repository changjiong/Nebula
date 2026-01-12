"""
Data Warehouse Adapter Module

Provides adapter for connecting to enterprise data warehouse (数仓) APIs.

Features:
- Query execution and result retrieval
- Batch data operations
- Schema and metadata discovery
- Data export capabilities
- Mock mode for testing
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.adapters.base import (
    AdapterConfig,
    AdapterError,
    AdapterRequest,
    HTTPAdapter,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


class QueryType(str, Enum):
    """Data warehouse query types"""

    SQL = "sql"
    STORED_PROCEDURE = "stored_procedure"
    BATCH_QUERY = "batch_query"
    EXPORT = "export"


class DataFormat(str, Enum):
    """Data output formats"""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    ARROW = "arrow"


class QueryStatus(str, Enum):
    """Query execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryRequest(BaseModel):
    """Data warehouse query request"""

    query: str = Field(..., description="SQL query or procedure name")
    query_type: QueryType = Field(default=QueryType.SQL, description="Query type")
    params: dict[str, Any] | None = Field(
        default=None, description="Query parameters"
    )
    database: str | None = Field(default=None, description="Target database")
    schema_name: str | None = Field(default=None, description="Target schema")
    limit: int | None = Field(default=None, description="Result limit")
    timeout: int | None = Field(default=None, description="Query timeout in seconds")
    data_format: DataFormat = Field(
        default=DataFormat.JSON, description="Output format"
    )
    async_execution: bool = Field(
        default=False, description="Execute asynchronously"
    )


class QueryResult(BaseModel):
    """Data warehouse query result"""

    query_id: str = Field(..., description="Unique query identifier")
    status: QueryStatus = Field(..., description="Query status")
    rows_affected: int = Field(default=0, description="Number of affected rows")
    columns: list[str] = Field(default_factory=list, description="Column names")
    data: list[dict[str, Any]] = Field(default_factory=list, description="Result data")
    execution_time_ms: float = Field(default=0, description="Execution time")
    started_at: datetime | None = Field(default=None, description="Start timestamp")
    completed_at: datetime | None = Field(default=None, description="End timestamp")
    error_message: str | None = Field(default=None, description="Error if failed")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class TableInfo(BaseModel):
    """Table metadata information"""

    database: str = Field(..., description="Database name")
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    table_type: str = Field(default="TABLE", description="Table type")
    row_count: int | None = Field(default=None, description="Approximate row count")
    columns: list[dict[str, Any]] = Field(
        default_factory=list, description="Column definitions"
    )
    created_at: datetime | None = Field(default=None, description="Creation time")
    updated_at: datetime | None = Field(default=None, description="Last update time")


class DataWarehouseConfig(AdapterConfig):
    """Data warehouse specific configuration"""

    database: str = ""
    schema_name: str = "public"
    max_query_timeout: int = 300
    default_limit: int = 10000
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 3600


# ============================================================================
# Mock Data
# ============================================================================


MOCK_TABLES = [
    TableInfo(
        database="analytics",
        schema_name="public",
        table_name="customers",
        table_type="TABLE",
        row_count=150000,
        columns=[
            {"name": "id", "type": "BIGINT", "nullable": False},
            {"name": "name", "type": "VARCHAR(255)", "nullable": False},
            {"name": "email", "type": "VARCHAR(255)", "nullable": True},
            {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
        ],
    ),
    TableInfo(
        database="analytics",
        schema_name="public",
        table_name="transactions",
        table_type="TABLE",
        row_count=5000000,
        columns=[
            {"name": "id", "type": "BIGINT", "nullable": False},
            {"name": "customer_id", "type": "BIGINT", "nullable": False},
            {"name": "amount", "type": "DECIMAL(18,2)", "nullable": False},
            {"name": "transaction_date", "type": "DATE", "nullable": False},
        ],
    ),
    TableInfo(
        database="analytics",
        schema_name="public",
        table_name="loan_applications",
        table_type="TABLE",
        row_count=250000,
        columns=[
            {"name": "id", "type": "BIGINT", "nullable": False},
            {"name": "customer_id", "type": "BIGINT", "nullable": False},
            {"name": "amount_requested", "type": "DECIMAL(18,2)", "nullable": False},
            {"name": "status", "type": "VARCHAR(50)", "nullable": False},
            {"name": "applied_at", "type": "TIMESTAMP", "nullable": False},
        ],
    ),
]

MOCK_QUERY_RESULTS: dict[str, list[dict[str, Any]]] = {
    "customers": [
        {
            "id": 1,
            "name": "张三",
            "email": "zhangsan@example.com",
            "created_at": "2024-01-15T10:30:00Z",
        },
        {
            "id": 2,
            "name": "李四",
            "email": "lisi@example.com",
            "created_at": "2024-01-16T11:45:00Z",
        },
        {
            "id": 3,
            "name": "王五",
            "email": "wangwu@example.com",
            "created_at": "2024-01-17T09:15:00Z",
        },
    ],
    "transactions": [
        {
            "id": 1001,
            "customer_id": 1,
            "amount": 5000.00,
            "transaction_date": "2024-03-01",
        },
        {
            "id": 1002,
            "customer_id": 2,
            "amount": 12500.50,
            "transaction_date": "2024-03-02",
        },
        {
            "id": 1003,
            "customer_id": 1,
            "amount": 3200.00,
            "transaction_date": "2024-03-03",
        },
    ],
    "loan_applications": [
        {
            "id": 10001,
            "customer_id": 1,
            "amount_requested": 50000.00,
            "status": "approved",
            "applied_at": "2024-02-15T14:20:00Z",
        },
        {
            "id": 10002,
            "customer_id": 3,
            "amount_requested": 100000.00,
            "status": "pending",
            "applied_at": "2024-03-10T09:00:00Z",
        },
    ],
}


# ============================================================================
# Data Warehouse Adapter
# ============================================================================


class DataWarehouseAdapter(HTTPAdapter):
    """
    Data Warehouse API Adapter (数仓适配器)

    Provides unified interface for:
    - SQL query execution
    - Schema and metadata discovery
    - Batch data operations
    - Data export

    Usage:
        config = DataWarehouseConfig(
            base_url="http://datawarehouse.internal:8080",
            database="analytics",
            mock_mode=True  # For testing
        )
        adapter = DataWarehouseAdapter(config)

        # Execute query
        result = adapter.execute_query(QueryRequest(
            query="SELECT * FROM customers LIMIT 10"
        ))

        # Get table list
        tables = adapter.list_tables()
    """

    def __init__(self, config: DataWarehouseConfig | None = None):
        super().__init__(config or DataWarehouseConfig())
        self._dw_config: DataWarehouseConfig = self.config  # type: ignore
        self._query_counter = 0

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        self._query_counter += 1
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        return f"dw-query-{timestamp}-{self._query_counter}"

    # -------------------------------------------------------------------------
    # Mock Response Generators
    # -------------------------------------------------------------------------

    def _mock_execute_query(self, request: QueryRequest) -> QueryResult:
        """Generate mock query result"""
        query_id = self._generate_query_id()
        now = datetime.now(timezone.utc)

        # Parse table name from query for mock data
        query_lower = request.query.lower()
        table_data: list[dict[str, Any]] = []
        columns: list[str] = []

        for table_name, data in MOCK_QUERY_RESULTS.items():
            if table_name in query_lower:
                table_data = data[: request.limit] if request.limit else data
                columns = list(data[0].keys()) if data else []
                break

        if not table_data:
            # Default mock data
            table_data = [{"result": "mock_data", "count": 100}]
            columns = ["result", "count"]

        return QueryResult(
            query_id=query_id,
            status=QueryStatus.COMPLETED,
            rows_affected=len(table_data),
            columns=columns,
            data=table_data,
            execution_time_ms=150.5,
            started_at=now,
            completed_at=now,
            metadata={
                "mock": True,
                "query": request.query[:100],
                "database": request.database or self._dw_config.database,
            },
        )

    def _mock_list_tables(
        self, database: str | None, schema_name: str | None
    ) -> list[TableInfo]:
        """Generate mock table list"""
        tables = MOCK_TABLES.copy()
        if database:
            tables = [t for t in tables if t.database == database]
        if schema_name:
            tables = [t for t in tables if t.schema_name == schema_name]
        return tables

    def _mock_get_table_info(self, table_name: str) -> TableInfo | None:
        """Get mock table info"""
        for table in MOCK_TABLES:
            if table.table_name == table_name:
                return table
        return None

    # -------------------------------------------------------------------------
    # Query Execution
    # -------------------------------------------------------------------------

    def execute_query(self, request: QueryRequest) -> QueryResult:
        """
        Execute a data warehouse query.

        Args:
            request: Query request with SQL and parameters

        Returns:
            QueryResult with data and metadata
        """
        if self.config.mock_mode:
            logger.info(f"[DataWarehouse] Mock query: {request.query[:50]}...")
            return self._mock_execute_query(request)

        adapter_request = AdapterRequest(
            endpoint="/api/v1/query",
            method="POST",
            body={
                "query": request.query,
                "query_type": request.query_type.value,
                "params": request.params,
                "database": request.database or self._dw_config.database,
                "schema": request.schema_name or self._dw_config.schema_name,
                "limit": request.limit or self._dw_config.default_limit,
                "timeout": request.timeout or self._dw_config.max_query_timeout,
                "format": request.data_format.value,
                "async": request.async_execution,
            },
        )

        response = self.call(adapter_request)
        if response.error:
            raise AdapterError(
                message=f"Query failed: {response.error}",
                error_code=response.error_code,
            )

        return QueryResult(**response.data) if response.data else QueryResult(
            query_id=self._generate_query_id(),
            status=QueryStatus.FAILED,
            error_message="Empty response",
        )

    async def async_execute_query(self, request: QueryRequest) -> QueryResult:
        """Async version of execute_query"""
        if self.config.mock_mode:
            logger.info(f"[DataWarehouse] Mock async query: {request.query[:50]}...")
            return self._mock_execute_query(request)

        adapter_request = AdapterRequest(
            endpoint="/api/v1/query",
            method="POST",
            body={
                "query": request.query,
                "query_type": request.query_type.value,
                "params": request.params,
                "database": request.database or self._dw_config.database,
                "schema": request.schema_name or self._dw_config.schema_name,
                "limit": request.limit or self._dw_config.default_limit,
                "timeout": request.timeout or self._dw_config.max_query_timeout,
                "format": request.data_format.value,
                "async": request.async_execution,
            },
        )

        response = await self.async_call(adapter_request)
        if response.error:
            raise AdapterError(
                message=f"Query failed: {response.error}",
                error_code=response.error_code,
            )

        return QueryResult(**response.data) if response.data else QueryResult(
            query_id=self._generate_query_id(),
            status=QueryStatus.FAILED,
            error_message="Empty response",
        )

    # -------------------------------------------------------------------------
    # Schema Discovery
    # -------------------------------------------------------------------------

    def list_tables(
        self, database: str | None = None, schema_name: str | None = None
    ) -> list[TableInfo]:
        """
        List tables in the data warehouse.

        Args:
            database: Filter by database name
            schema_name: Filter by schema name

        Returns:
            List of TableInfo objects
        """
        if self.config.mock_mode:
            return self._mock_list_tables(database, schema_name)

        adapter_request = AdapterRequest(
            endpoint="/api/v1/schema/tables",
            method="GET",
            params={
                "database": database or self._dw_config.database,
                "schema": schema_name or self._dw_config.schema_name,
            },
        )

        response = self.call(adapter_request)
        if response.error:
            raise AdapterError(
                message=f"Failed to list tables: {response.error}",
                error_code=response.error_code,
            )

        return [TableInfo(**t) for t in (response.data or [])]

    async def async_list_tables(
        self, database: str | None = None, schema_name: str | None = None
    ) -> list[TableInfo]:
        """Async version of list_tables"""
        if self.config.mock_mode:
            return self._mock_list_tables(database, schema_name)

        adapter_request = AdapterRequest(
            endpoint="/api/v1/schema/tables",
            method="GET",
            params={
                "database": database or self._dw_config.database,
                "schema": schema_name or self._dw_config.schema_name,
            },
        )

        response = await self.async_call(adapter_request)
        if response.error:
            raise AdapterError(
                message=f"Failed to list tables: {response.error}",
                error_code=response.error_code,
            )

        return [TableInfo(**t) for t in (response.data or [])]

    def get_table_info(self, table_name: str) -> TableInfo | None:
        """
        Get detailed information about a specific table.

        Args:
            table_name: Name of the table

        Returns:
            TableInfo or None if not found
        """
        if self.config.mock_mode:
            return self._mock_get_table_info(table_name)

        adapter_request = AdapterRequest(
            endpoint=f"/api/v1/schema/tables/{table_name}",
            method="GET",
            params={"database": self._dw_config.database},
        )

        response = self.call(adapter_request)
        if response.error:
            return None

        return TableInfo(**response.data) if response.data else None

    # -------------------------------------------------------------------------
    # Data Export
    # -------------------------------------------------------------------------

    def export_data(
        self,
        query: str,
        format: DataFormat = DataFormat.CSV,  # noqa: A002
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Export query results in specified format.

        Args:
            query: SQL query to export
            format: Output format (CSV, JSON, PARQUET)
            limit: Maximum rows to export

        Returns:
            Export result with download info
        """
        if self.config.mock_mode:
            return {
                "export_id": f"export-{self._generate_query_id()}",
                "status": "completed",
                "format": format.value,
                "row_count": limit or 1000,
                "download_url": "https://mock.example.com/export/download",
                "expires_at": "2024-12-31T23:59:59Z",
            }

        adapter_request = AdapterRequest(
            endpoint="/api/v1/export",
            method="POST",
            body={
                "query": query,
                "format": format.value,
                "limit": limit,
            },
        )

        response = self.call(adapter_request)
        if response.error:
            raise AdapterError(
                message=f"Export failed: {response.error}",
                error_code=response.error_code,
            )

        return response.data or {}

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        """
        Check connection health to data warehouse.

        Returns:
            Health status information
        """
        if self.config.mock_mode:
            return {
                "status": "healthy",
                "database": self._dw_config.database,
                "schema": self._dw_config.schema_name,
                "mock_mode": True,
            }

        adapter_request = AdapterRequest(
            endpoint="/api/v1/health",
            method="GET",
        )

        response = self.call(adapter_request)
        return {
            "status": "healthy" if not response.error else "unhealthy",
            "error": response.error,
            "latency_ms": response.latency_ms,
        }

"""
Base Adapter Module

Provides the foundation for all external service adapters with:
- Unified request/response format
- Synchronous and asynchronous call support
- Timeout handling and error retry
- Mock mode for testing
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar

import httpx
from pydantic import BaseModel, Field
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================


class AdapterStatus(str, Enum):
    """Adapter call status"""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    MOCK = "mock"


class RetryStrategy(str, Enum):
    """Retry strategy options"""

    NONE = "none"
    EXPONENTIAL = "exponential"
    FIXED = "fixed"


# ============================================================================
# Request/Response Models
# ============================================================================


class AdapterRequest(BaseModel):
    """Unified adapter request format"""

    endpoint: str = Field(..., description="API endpoint or operation name")
    method: str = Field(default="GET", description="HTTP method (GET, POST, etc.)")
    params: dict[str, Any] | None = Field(
        default=None, description="Query parameters"
    )
    body: dict[str, Any] | None = Field(default=None, description="Request body")
    headers: dict[str, str] | None = Field(
        default=None, description="Additional headers"
    )
    timeout: float | None = Field(
        default=None, description="Request timeout in seconds"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional request metadata"
    )

    model_config = {"extra": "allow"}


T = TypeVar("T")


class AdapterResponse(BaseModel, Generic[T]):
    """Unified adapter response format"""

    status: AdapterStatus = Field(..., description="Response status")
    data: T | None = Field(default=None, description="Response data")
    error: str | None = Field(default=None, description="Error message if failed")
    error_code: str | None = Field(default=None, description="Error code if failed")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp",
    )
    latency_ms: float = Field(default=0, description="Request latency in milliseconds")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )

    model_config = {"extra": "allow"}


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class AdapterConfig:
    """Adapter configuration"""

    base_url: str = ""
    timeout: float = 30.0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_min_wait: float = 1.0
    retry_max_wait: float = 10.0
    mock_mode: bool = False
    mock_delay: float = 0.1
    headers: dict[str, str] = field(default_factory=dict)
    auth_token: str | None = None


# ============================================================================
# Exceptions
# ============================================================================


class AdapterError(Exception):
    """Base exception for adapter errors"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AdapterTimeoutError(AdapterError):
    """Timeout error"""

    def __init__(self, message: str = "Request timed out", timeout: float = 0):
        super().__init__(message, error_code="TIMEOUT")
        self.timeout = timeout


class AdapterConnectionError(AdapterError):
    """Connection error"""

    def __init__(self, message: str = "Connection failed"):
        super().__init__(message, error_code="CONNECTION_ERROR")


class AdapterRetryExhaustedError(AdapterError):
    """All retries exhausted"""

    def __init__(self, message: str = "All retries exhausted", attempts: int = 0):
        super().__init__(message, error_code="RETRY_EXHAUSTED")
        self.attempts = attempts


# ============================================================================
# Base Adapter
# ============================================================================


class BaseAdapter(ABC):
    """
    Abstract base class for all external service adapters.

    Features:
    - Unified request/response format
    - Synchronous and asynchronous call methods
    - Configurable timeout and retry logic
    - Mock mode for testing

    Usage:
        class MyAdapter(BaseAdapter):
            def _process_request(self, request):
                # Process and return response data
                return {"result": "ok"}

            async def _async_process_request(self, request):
                # Async version
                return {"result": "ok"}

        adapter = MyAdapter(AdapterConfig(base_url="http://api.example.com"))
        response = adapter.call(AdapterRequest(endpoint="/users"))
    """

    def __init__(self, config: AdapterConfig | None = None):
        self.config = config or AdapterConfig()
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None
        self._request_counter = 0
        self._mock_responses: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Adapter name for logging"""
        return self.__class__.__name__

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        self._request_counter += 1
        timestamp = int(time.time() * 1000)
        return f"{self.name}-{timestamp}-{self._request_counter}"

    # -------------------------------------------------------------------------
    # HTTP Client Management
    # -------------------------------------------------------------------------

    def _get_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client"""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._build_headers(),
            )
        return self._client

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._build_headers(),
            )
        return self._async_client

    def _build_headers(self) -> dict[str, str]:
        """Build request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.config.headers,
        }
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        return headers

    def close(self) -> None:
        """Close HTTP clients"""
        if self._client:
            self._client.close()
            self._client = None

    async def aclose(self) -> None:
        """Close async HTTP clients"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    # -------------------------------------------------------------------------
    # Mock Mode
    # -------------------------------------------------------------------------

    def set_mock_response(self, endpoint: str, response: Any) -> None:
        """Set mock response for an endpoint"""
        self._mock_responses[endpoint] = response

    def clear_mock_responses(self) -> None:
        """Clear all mock responses"""
        self._mock_responses.clear()

    def _get_mock_response(self, request: AdapterRequest) -> Any:
        """Get mock response for request"""
        if request.endpoint in self._mock_responses:
            return self._mock_responses[request.endpoint]
        return self._default_mock_response(request)

    def _default_mock_response(self, request: AdapterRequest) -> dict[str, Any]:
        """Default mock response when no specific mock is set"""
        return {
            "mock": True,
            "endpoint": request.endpoint,
            "method": request.method,
            "message": "Default mock response",
        }

    # -------------------------------------------------------------------------
    # Abstract Methods (to be implemented by subclasses)
    # -------------------------------------------------------------------------

    @abstractmethod
    def _process_request(self, request: AdapterRequest) -> Any:
        """
        Process the request and return response data.
        Must be implemented by subclasses.

        Args:
            request: The adapter request

        Returns:
            Response data (will be wrapped in AdapterResponse)

        Raises:
            AdapterError: On processing failure
        """
        pass

    @abstractmethod
    async def _async_process_request(self, request: AdapterRequest) -> Any:
        """
        Async version of _process_request.
        Must be implemented by subclasses.

        Args:
            request: The adapter request

        Returns:
            Response data (will be wrapped in AdapterResponse)

        Raises:
            AdapterError: On processing failure
        """
        pass

    # -------------------------------------------------------------------------
    # Retry Logic
    # -------------------------------------------------------------------------

    def _create_retry_decorator(self):
        """Create retry decorator based on config"""
        if self.config.retry_strategy == RetryStrategy.NONE:
            return lambda f: f

        return retry(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                min=self.config.retry_min_wait, max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type(
                (httpx.TimeoutException, httpx.ConnectError, AdapterConnectionError)
            ),
            reraise=True,
        )

    def _execute_with_retry(self, request: AdapterRequest) -> Any:
        """Execute request with retry logic"""
        retry_decorator = self._create_retry_decorator()
        retryable_func = retry_decorator(self._process_request)

        try:
            return retryable_func(request)
        except RetryError as e:
            raise AdapterRetryExhaustedError(
                f"All {self.config.max_retries} retries exhausted",
                attempts=self.config.max_retries,
            ) from e

    async def _async_execute_with_retry(self, request: AdapterRequest) -> Any:
        """Execute async request with retry logic"""
        retry_decorator = self._create_retry_decorator()
        retryable_func = retry_decorator(self._async_process_request)

        try:
            return await retryable_func(request)
        except RetryError as e:
            raise AdapterRetryExhaustedError(
                f"All {self.config.max_retries} retries exhausted",
                attempts=self.config.max_retries,
            ) from e

    # -------------------------------------------------------------------------
    # Main Call Methods
    # -------------------------------------------------------------------------

    def call(self, request: AdapterRequest) -> AdapterResponse[Any]:
        """
        Synchronous call to external service.

        Args:
            request: The adapter request

        Returns:
            AdapterResponse with status, data, and metadata
        """
        request_id = self._generate_request_id()
        start_time = time.time()

        logger.info(
            f"[{self.name}] Starting request {request_id}: "
            f"{request.method} {request.endpoint}"
        )

        try:
            # Mock mode
            if self.config.mock_mode:
                time.sleep(self.config.mock_delay)
                data = self._get_mock_response(request)
                latency = (time.time() - start_time) * 1000

                logger.info(f"[{self.name}] Mock response for {request_id}")
                return AdapterResponse(
                    status=AdapterStatus.MOCK,
                    data=data,
                    request_id=request_id,
                    latency_ms=latency,
                    metadata={"mock": True},
                )

            # Execute with retry
            data = self._execute_with_retry(request)
            latency = (time.time() - start_time) * 1000

            logger.info(
                f"[{self.name}] Request {request_id} completed in {latency:.2f}ms"
            )

            return AdapterResponse(
                status=AdapterStatus.SUCCESS,
                data=data,
                request_id=request_id,
                latency_ms=latency,
            )

        except AdapterTimeoutError as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[{self.name}] Request {request_id} timed out: {e.message}")
            return AdapterResponse(
                status=AdapterStatus.TIMEOUT,
                error=e.message,
                error_code=e.error_code,
                request_id=request_id,
                latency_ms=latency,
            )

        except AdapterError as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"[{self.name}] Request {request_id} failed: {e.message}")
            return AdapterResponse(
                status=AdapterStatus.ERROR,
                error=e.message,
                error_code=e.error_code,
                request_id=request_id,
                latency_ms=latency,
                metadata={"details": e.details},
            )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.exception(f"[{self.name}] Unexpected error in {request_id}")
            return AdapterResponse(
                status=AdapterStatus.ERROR,
                error=str(e),
                error_code="UNEXPECTED_ERROR",
                request_id=request_id,
                latency_ms=latency,
            )

    async def async_call(self, request: AdapterRequest) -> AdapterResponse[Any]:
        """
        Asynchronous call to external service.

        Args:
            request: The adapter request

        Returns:
            AdapterResponse with status, data, and metadata
        """
        request_id = self._generate_request_id()
        start_time = time.time()

        logger.info(
            f"[{self.name}] Starting async request {request_id}: "
            f"{request.method} {request.endpoint}"
        )

        try:
            # Mock mode
            if self.config.mock_mode:
                await asyncio.sleep(self.config.mock_delay)
                data = self._get_mock_response(request)
                latency = (time.time() - start_time) * 1000

                logger.info(f"[{self.name}] Mock response for {request_id}")
                return AdapterResponse(
                    status=AdapterStatus.MOCK,
                    data=data,
                    request_id=request_id,
                    latency_ms=latency,
                    metadata={"mock": True},
                )

            # Execute with retry
            data = await self._async_execute_with_retry(request)
            latency = (time.time() - start_time) * 1000

            logger.info(
                f"[{self.name}] Async request {request_id} completed in {latency:.2f}ms"
            )

            return AdapterResponse(
                status=AdapterStatus.SUCCESS,
                data=data,
                request_id=request_id,
                latency_ms=latency,
            )

        except AdapterTimeoutError as e:
            latency = (time.time() - start_time) * 1000
            logger.error(
                f"[{self.name}] Async request {request_id} timed out: {e.message}"
            )
            return AdapterResponse(
                status=AdapterStatus.TIMEOUT,
                error=e.message,
                error_code=e.error_code,
                request_id=request_id,
                latency_ms=latency,
            )

        except AdapterError as e:
            latency = (time.time() - start_time) * 1000
            logger.error(
                f"[{self.name}] Async request {request_id} failed: {e.message}"
            )
            return AdapterResponse(
                status=AdapterStatus.ERROR,
                error=e.message,
                error_code=e.error_code,
                request_id=request_id,
                latency_ms=latency,
                metadata={"details": e.details},
            )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.exception(f"[{self.name}] Unexpected error in async {request_id}")
            return AdapterResponse(
                status=AdapterStatus.ERROR,
                error=str(e),
                error_code="UNEXPECTED_ERROR",
                request_id=request_id,
                latency_ms=latency,
            )

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> AdapterResponse[Any]:
        """Convenience method for GET requests"""
        return self.call(AdapterRequest(endpoint=endpoint, method="GET", params=params))

    def post(
        self, endpoint: str, body: dict[str, Any] | None = None
    ) -> AdapterResponse[Any]:
        """Convenience method for POST requests"""
        return self.call(AdapterRequest(endpoint=endpoint, method="POST", body=body))

    async def async_get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> AdapterResponse[Any]:
        """Convenience method for async GET requests"""
        return await self.async_call(
            AdapterRequest(endpoint=endpoint, method="GET", params=params)
        )

    async def async_post(
        self, endpoint: str, body: dict[str, Any] | None = None
    ) -> AdapterResponse[Any]:
        """Convenience method for async POST requests"""
        return await self.async_call(
            AdapterRequest(endpoint=endpoint, method="POST", body=body)
        )


# ============================================================================
# HTTP Adapter (Generic HTTP-based adapter)
# ============================================================================


class HTTPAdapter(BaseAdapter):
    """
    Generic HTTP adapter for RESTful APIs.

    Provides a ready-to-use implementation that makes actual HTTP calls.
    Can be subclassed for specific API customizations.
    """

    def _process_request(self, request: AdapterRequest) -> Any:
        """Process HTTP request synchronously"""
        client = self._get_client()
        timeout = request.timeout or self.config.timeout

        try:
            response = client.request(
                method=request.method,
                url=request.endpoint,
                params=request.params,
                json=request.body,
                headers=request.headers or {},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else None

        except httpx.TimeoutException as e:
            raise AdapterTimeoutError(
                f"Request to {request.endpoint} timed out after {timeout}s",
                timeout=timeout,
            ) from e

        except httpx.ConnectError as e:
            raise AdapterConnectionError(
                f"Failed to connect to {request.endpoint}: {e}"
            ) from e

        except httpx.HTTPStatusError as e:
            raise AdapterError(
                message=f"HTTP {e.response.status_code}: {e.response.text}",
                error_code=f"HTTP_{e.response.status_code}",
                details={"response": e.response.text},
            ) from e

    async def _async_process_request(self, request: AdapterRequest) -> Any:
        """Process HTTP request asynchronously"""
        client = await self._get_async_client()
        timeout = request.timeout or self.config.timeout

        try:
            response = await client.request(
                method=request.method,
                url=request.endpoint,
                params=request.params,
                json=request.body,
                headers=request.headers or {},
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else None

        except httpx.TimeoutException as e:
            raise AdapterTimeoutError(
                f"Request to {request.endpoint} timed out after {timeout}s",
                timeout=timeout,
            ) from e

        except httpx.ConnectError as e:
            raise AdapterConnectionError(
                f"Failed to connect to {request.endpoint}: {e}"
            ) from e

        except httpx.HTTPStatusError as e:
            raise AdapterError(
                message=f"HTTP {e.response.status_code}: {e.response.text}",
                error_code=f"HTTP_{e.response.status_code}",
                details={"response": e.response.text},
            ) from e

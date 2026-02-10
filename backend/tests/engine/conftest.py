"""
Pytest configuration for engine tests.

Configures pytest to only use asyncio backend for async tests.
"""

import pytest


# Configure anyio to only use asyncio (not trio)
@pytest.fixture
def anyio_backend():
    return "asyncio"

"""
Checkpointer Module - LangGraph State Persistence

This module provides PostgreSQL-based checkpointing for LangGraph graphs,
enabling state persistence, recovery, and time-travel debugging.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from app.core.config import settings


# Global checkpointer instance (singleton)
_checkpointer: AsyncPostgresSaver | None = None
_checkpointer_initialized: bool = False


def _get_postgres_conninfo() -> str:
    """Build PostgreSQL connection info string from settings."""
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


async def get_checkpointer() -> AsyncPostgresSaver:
    """
    Get or create the async PostgreSQL checkpointer.

    Returns a singleton instance of AsyncPostgresSaver connected to
    the application's PostgreSQL database.

    The checkpointer is automatically initialized (tables created)
    on first use.
    """
    global _checkpointer, _checkpointer_initialized

    if _checkpointer is None:
        conninfo = _get_postgres_conninfo()
        _checkpointer = AsyncPostgresSaver.from_conn_string(conninfo)

    if not _checkpointer_initialized:
        await _checkpointer.setup()
        _checkpointer_initialized = True

    return _checkpointer


@asynccontextmanager
async def checkpointer_context() -> AsyncGenerator[AsyncPostgresSaver, None]:
    """
    Context manager for checkpointer with proper cleanup.

    Usage:
        async with checkpointer_context() as checkpointer:
            graph = compile_nfc_graph(gateway, checkpointer=checkpointer)
    """
    checkpointer = await get_checkpointer()
    try:
        yield checkpointer
    finally:
        # Cleanup if needed (connection pooling handles this)
        pass


async def close_checkpointer() -> None:
    """Close the checkpointer connection (for shutdown)."""
    global _checkpointer, _checkpointer_initialized

    if _checkpointer is not None:
        # AsyncPostgresSaver manages its own connection pool
        _checkpointer = None
        _checkpointer_initialized = False

"""Redis connection pool and key constants."""
import os
import json
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

# Redis connection pool (lazy init)
_pool: Optional[aioredis.ConnectionPool] = None
_redis: Optional[Redis] = None

# --- Key Constants ---

# Window stack order: JSON array of window IDs from bottom to top
KEY_WINDOW_STACK = "window_stack"

# Active window IDs: Set of currently active window IDs
KEY_ACTIVE_WINDOWS = "active_windows"

# Streaming request lock: TTL 300s, prevents duplicate streaming requests
KEY_STREAMING_PREFIX = "streaming"  # streaming:{id}

# Session message cache: TTL 3600s, stores latest 20 messages as JSON
KEY_SESSION_PREFIX = "session"  # session:{id}


def _redis_url() -> str:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    password = os.getenv("REDIS_PASSWORD", "")
    db = os.getenv("REDIS_DB", "0")
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


async def get_redis() -> Redis:
    """Get or create a Redis connection from the pool."""
    global _pool, _redis
    if _redis is None:
        _pool = aioredis.ConnectionPool.from_url(
            _redis_url(),
            max_connections=10,
            decode_responses=True,
        )
        _redis = Redis(connection_pool=_pool)
    return _redis


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global _redis, _pool
    if _redis:
        await _redis.close()
        _redis = None
    if _pool:
        await _pool.disconnect()
        _pool = None


# --- Key helpers ---

def streaming_key(window_id: str) -> str:
    """Key for streaming request lock."""
    return f"{KEY_STREAMING_PREFIX}:{window_id}"


def session_key(window_id: str) -> str:
    """Key for session message cache."""
    return f"{KEY_SESSION_PREFIX}:{window_id}"


# TTL constants
STREAMING_TTL = 300    # 5 minutes
SESSION_TTL = 3600     # 1 hour

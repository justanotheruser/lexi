import json
from typing import Any

import redis.asyncio as redis
from loguru import logger

from app.ports.cache import Cache


class RedisCache(Cache):
    """Redis-based cache implementation"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: redis.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self._redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            logger.info("Disconnected from Redis")

    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set a key-value pair in cache"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            await self._redis.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            raise

    async def get(self, key: str) -> Any:
        """Get a value from cache by key"""
        if not self._redis:
            raise RuntimeError("Redis not connected")
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    async def delete(self, key: str) -> None:
        """Delete a key from cache"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            raise

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of cache key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration time for a key"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            await self._redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Failed to set expiration for cache key {key}: {e}")
            raise

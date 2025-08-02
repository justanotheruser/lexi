import asyncio
import time
from typing import Any, Dict, Optional, Tuple

from app.ports.cache import Cache


class InMemoryCache(Cache):
    """For tests and debugging"""

    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()

    def _start_cleanup_task(self) -> None:
        """Start background task to clean up expired entries"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())

    async def _cleanup_expired(self) -> None:
        """Background task to remove expired cache entries"""
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key
                    for key, (_, expiry) in self._cache.items()
                    if expiry is not None and current_time > expiry
                ]

                for key in expired_keys:
                    del self._cache[key]

                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error if needed, but continue cleanup
                await asyncio.sleep(1)

    def _is_expired(self, key: str) -> bool:
        """Check if a key is expired"""
        if key not in self._cache:
            return True

        _, expiry = self._cache[key]
        if expiry is None:
            return False

        return time.time() > expiry

    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set a key-value pair with TTL in seconds"""
        expiry = time.time() + ttl if ttl > 0 else None
        self._cache[key] = (value, expiry)

    async def get(self, key: str) -> Any:
        """Get a value by key, returns None if not found or expired"""
        if self._is_expired(key):
            if key in self._cache:
                del self._cache[key]
            return None

        value, _ = self._cache[key]
        return value

    async def delete(self, key: str) -> None:
        """Delete a key from the cache"""
        if key in self._cache:
            del self._cache[key]

    async def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired"""
        return not self._is_expired(key)

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration time for an existing key"""
        if key in self._cache:
            value, _ = self._cache[key]
            expiry = time.time() + ttl if ttl > 0 else None
            self._cache[key] = (value, expiry)

    async def close(self) -> None:
        """Clean up resources"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

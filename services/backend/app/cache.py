"""
Alfred - Enterprise AI Credit Governance Platform
High-Performance Caching Subsystem

[ARCHITECTURAL ROLE]
This module provides a critical latency-reduction layer between the API and
the persistent storage (Database). It utilizes Redis for distributed caching,
allowing the platform to scale horizontally while maintaining consistent
performance for high-frequency operations like quota checks and leaderboard reads.

"""

import json
from functools import wraps
from typing import Any, Callable, Optional

# Conditionally import redis to support environments where it is optional
try:
    import redis
except ImportError:
    redis = None

from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


class CacheManager:
    """
    Stateful Cache Coordinator.

    Handles connection lifecycle, serialization/deserialization of complex objects,
    and provides a unified interface for key-value storage operations.
    """

    def __init__(self):
        """
        Bootstrap the Redist connection with aggressive timeouts.
        Aggressive timeouts ensure that a slow cache doesn't block critical request paths.
        """
        if settings.redis_enabled and redis:
            try:
                self.redis = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2,  # Fast fail on connect
                    socket_timeout=2,  # Fast fail on command
                )
                # Heartbeat verification
                self.redis.ping()
                logger.info(
                    f"Performance Optimization: Redis Cache Active @ {settings.redis_host}:{settings.redis_port}"
                )
            except Exception as e:
                logger.warning(
                    f"Cache Degradation: Redis connection failed ({e}). Reverting to Database-Only mode."
                )
                self.redis = None
        else:
            self.redis = None
            if settings.redis_enabled and not redis:
                logger.error(
                    "Configuration Conflict: Redis enabled but 'redis-py' package missing."
                )
            else:
                logger.info("Operational Mode: Caching Disabled (Direct-to-DB).")

    def get(self, key: str) -> Optional[Any]:
        """
        Lookup with automatic JSON hydration.
        Returns None on miss or cache-failure.
        """
        if not self.redis:
            return None

        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache Interruption (GET): {e}")

        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Persistent set with mandatory TTL (Default 5 mins).
        We enforce TTL to prevent the cache from becoming a 'Stale Ghost' of the DB.
        """
        if not self.redis:
            return False

        try:
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache Interruption (SET): {e}")
            return False

    def delete(self, key: str) -> bool:
        """Atomic key invalidation."""
        if not self.redis:
            return False

        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache Interruption (DELETE): {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Mass Invalidation via Pattern Matching.
        Useful for clearing all caches related to a specific user or team
        when their permissions change.
        """
        if not self.redis:
            return 0

        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache Interruption (INVALIDATE): {e}")

        return 0


cache = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    High-Order Memoization Decorator.

    Automates the 'Cache-Aside' pattern for repository methods.

    Note: Ensure that decorated function arguments are serializable (strings/ints).
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Compute a Deterministic Key based on function signature and arguments
            cache_key = f"alfred:{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 1. Attempt Retrieval (Fast Path)
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"⚡ Cache Hit: {cache_key}")
                return cached_value

            # 2. Source of Truth (Slow Path)
            logger.debug(f"🕳️ Cache Miss: {cache_key}")
            result = func(*args, **kwargs)

            # 3. Asynchronously Populate Cache
            # (In this sync implementation, we wait, but failures are swallowed)
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator

"""
Alfred - Enterprise AI Credit Governance Platform
High-Performance Caching Subsystem

[ARCHITECTURAL ROLE]
This module provides a critical latency-reduction layer between the API and
the persistent storage (Database). It utilizes Redis for distributed caching,
allowing the platform to scale horizontally while maintaining consistent
performance for high-frequency operations like quota checks and leaderboard reads.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module provides a Redis-backed cache manager and decorator for high-frequency, low-latency operations. It gracefully degrades to DB-only mode if Redis is unavailable.
# Why: Caching is essential for performance and scalability in distributed systems.
# Root Cause: Without caching, DB load and latency would be unacceptably high for quota and analytics endpoints.
# Context: All cache logic should use this module. Future: consider async cache and distributed invalidation.
# Model Suitability: For cache patterns, GPT-4.1 is sufficient; for advanced distributed cache, a more advanced model may be preferred.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Manages Redis connection, serialization, and unified cache interface. Handles connection failures gracefully.
    # Why: Centralizes all cache logic and error handling.
    # Root Cause: Scattered cache logic leads to bugs and inconsistent performance.
    # Context: Used by all modules needing cache access.
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


# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Singleton cache instance for global use throughout the app.
# Why: Prevents multiple Redis connections and ensures consistent cache state.
# Root Cause: Multiple cache managers would cause race conditions and wasted resources.
# Context: Import and use this instance everywhere cache is needed.
cache = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Decorator for cache-aside pattern, memoizes function results in cache with TTL.
    # Why: Reduces DB load and improves response times for repeat queries.
    # Root Cause: Repeated expensive queries should be cached for efficiency.
    # Context: Use on repository or analytics methods that are read-heavy.
    """
    High-Order Memoization Decorator.

    Automates the 'Cache-Aside' pattern for repository methods.

    Note: Ensure that decorated function arguments are serializable (strings/ints).
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Compute a Deterministic Key based on function signature and arguments
            # Logic: prefix:func_name:normalized_args
            cache_key = f"alfred:{key_prefix}:{func.__name__}:{hash(str(args)+str(kwargs))}"

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

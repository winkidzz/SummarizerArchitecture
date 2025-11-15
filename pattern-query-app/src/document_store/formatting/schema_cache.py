"""
Schema caching for structured output generation.

Caches dynamically generated schemas to avoid redundant LLM calls
for similar documents.
"""
import time
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CachedSchema:
    """Represents a cached schema entry."""
    schema: Dict[str, Any]
    timestamp: float
    ttl: int
    hits: int = 0
    last_access: float = None

    def __post_init__(self):
        if self.last_access is None:
            self.last_access = self.timestamp

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return (time.time() - self.timestamp) > self.ttl

    def touch(self):
        """Update last access time and increment hit counter."""
        self.last_access = time.time()
        self.hits += 1


class SchemaCache:
    """
    LRU cache for generated schemas with TTL support.

    Features:
    - LRU eviction when max size reached
    - TTL-based expiration
    - Hit tracking for monitoring
    - Content-based hashing for cache keys
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize schema cache.

        Args:
            max_size: Maximum number of schemas to cache
            ttl_seconds: Time-to-live for cached schemas (default: 1 hour)
        """
        self.cache: Dict[str, CachedSchema] = {}
        self.max_size = max_size
        self.ttl = ttl_seconds

    def generate_key(
        self,
        content: str,
        schema_type: str,
        query: Optional[str] = None,
        sample_size: int = 1000
    ) -> str:
        """
        Generate cache key from content hash, schema type, and query.

        Args:
            content: Document content (uses first sample_size chars for hashing)
            schema_type: Type of schema (table, list, comparison, etc.)
            query: Optional query context
            sample_size: Number of characters to use for content hash

        Returns:
            Cache key string
        """
        # Use first N chars of content for hash (structure usually apparent early)
        content_sample = content[:sample_size]
        content_hash = hashlib.md5(content_sample.encode()).hexdigest()[:12]

        # Include query hash if provided
        query_part = ""
        if query:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            query_part = f":{query_hash}"

        return f"{content_hash}:{schema_type}{query_part}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached schema if available and not expired.

        Args:
            key: Cache key

        Returns:
            Cached schema dict or None if not found/expired
        """
        if key in self.cache:
            entry = self.cache[key]

            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                return None

            # Update access time and hits
            entry.touch()
            return entry.schema

        return None

    def set(self, key: str, schema: Dict[str, Any]):
        """
        Cache schema with automatic LRU eviction if needed.

        Args:
            key: Cache key
            schema: Schema dict to cache
        """
        # Evict LRU entry if at capacity
        if len(self.cache) >= self.max_size:
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].last_access
            )
            del self.cache[lru_key]

        # Add new entry
        self.cache[key] = CachedSchema(
            schema=schema,
            timestamp=time.time(),
            ttl=self.ttl
        )

    def clear(self):
        """Clear all cached schemas."""
        self.cache.clear()

    def clear_expired(self):
        """Remove expired entries from cache."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache size, total hits, and per-entry stats
        """
        self.clear_expired()  # Clean up first

        total_hits = sum(entry.hits for entry in self.cache.values())

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "ttl_seconds": self.ttl,
            "schemas": [
                {
                    "key": key,
                    "hits": entry.hits,
                    "age_seconds": int(time.time() - entry.timestamp),
                    "expires_in": int(entry.ttl - (time.time() - entry.timestamp))
                }
                for key, entry in self.cache.items()
            ]
        }

    def __len__(self) -> int:
        """Return number of cached schemas."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache (ignoring expiration)."""
        return key in self.cache

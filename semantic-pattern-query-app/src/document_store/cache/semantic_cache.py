"""
Layer 7: Semantic Caching

Redis-based semantic cache for query similarity matching.
Reduces costs and improves response times for similar queries.
"""

from typing import Optional, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import hashlib
import os
import logging
from datetime import datetime

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class HealthcareSemanticCache:
    """
    Semantic cache for common queries.
    
    Uses cosine similarity to match semantically similar queries
    and return cached responses.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        cache_ttl: int = 3600,
        similarity_threshold: float = 0.92
    ):
        """
        Initialize semantic cache.
        
        Args:
            host: Redis host (default: from env or localhost)
            port: Redis port
            password: Optional Redis password
            db: Redis database number
            cache_ttl: Cache TTL in seconds
            similarity_threshold: Similarity threshold for cache hits
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is not installed. "
                "Install it with: pip install redis"
            )
        
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6380"))  # Use port 6380 to avoid conflict
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.db = db or int(os.getenv("REDIS_DB", "0"))
        self.cache_ttl = cache_ttl or int(os.getenv("CACHE_TTL", "3600"))
        self.similarity_threshold = similarity_threshold or float(
            os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.92")
        )
        
        # Initialize Redis client
        # For local development, don't require password
        redis_kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "decode_responses": True,
            "socket_connect_timeout": 2,
            "socket_timeout": 2
        }
        
        # Only add password if explicitly provided
        if self.password:
            redis_kwargs["password"] = self.password
        
        # Try to connect
        self.redis_client = redis.Redis(**redis_kwargs)
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info(
                f"SemanticCache initialized: {self.host}:{self.port}, "
                f"TTL={self.cache_ttl}s, threshold={self.similarity_threshold}"
            )
        except (redis.AuthenticationError, redis.ConnectionError) as e:
            logger.warning(f"Redis connection issue: {e}")
            logger.warning("Cache will be disabled - queries will still work but without caching")
            # Set a flag to disable caching
            self.redis_client = None
            self._cache_disabled = True
            return
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            logger.warning("Cache will be disabled - queries will still work but without caching")
            self.redis_client = None
            self._cache_disabled = True
            return
        
        self._cache_disabled = False
    
    def get(
        self,
        query: str,
        query_embedding: np.ndarray,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check cache for semantically similar queries.
        
        Args:
            query: Query text
            query_embedding: Query embedding vector
            user_context: Optional user context for cache key
            
        Returns:
            Cached result if found, None otherwise
        """
        if self._cache_disabled or self.redis_client is None:
            return None
        # Build cache key prefix
        context_key = ""
        if user_context:
            # Include relevant context in cache key
            org_id = user_context.get("organization_id", "")
            context_key = f":{org_id}"
        
        cache_key_prefix = f"cache{context_key}:"
        
        # Search for similar queries
        try:
            # Get all cache keys with this prefix
            cache_keys = list(self.redis_client.scan_iter(match=f"{cache_key_prefix}*"))
            
            best_match = None
            best_similarity = 0.0
            
            for cached_key in cache_keys:
                try:
                    cached_data_str = self.redis_client.get(cached_key)
                    if not cached_data_str:
                        continue
                    
                    cached_data = json.loads(cached_data_str)
                    cached_embedding = np.array(cached_data.get("query_embedding", []))
                    
                    if len(cached_embedding) == 0 or len(cached_embedding) != len(query_embedding):
                        continue
                    
                    # Calculate similarity
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        cached_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity > best_similarity and similarity >= self.similarity_threshold:
                        best_similarity = similarity
                        best_match = {
                            "answer": cached_data.get("answer", ""),
                            "sources": cached_data.get("sources", []),
                            "cached": True,
                            "cache_key": cached_key,
                            "similarity": float(similarity)
                        }
                
                except Exception as e:
                    logger.debug(f"Error checking cache key {cached_key}: {e}")
                    continue
            
            if best_match:
                logger.info(
                    f"Cache hit: similarity={best_similarity:.3f}, "
                    f"key={best_match['cache_key']}"
                )
                return best_match
            
        except Exception as e:
            logger.warning(f"Error checking cache: {e}")
        
        return None
    
    def set(
        self,
        query: str,
        query_embedding: np.ndarray,
        result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ):
        """
        Cache result.
        
        Args:
            query: Query text
            query_embedding: Query embedding vector
            result: Result dictionary with answer and sources
            user_context: Optional user context for cache key
        """
        if self._cache_disabled or self.redis_client is None:
            return
        # Build cache key
        context_key = ""
        if user_context:
            org_id = user_context.get("organization_id", "")
            context_key = f":{org_id}"
        
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        cache_key = f"cache{context_key}:{query_hash}"
        
        # Prepare cache data
        cache_data = {
            "query": query,
            "query_embedding": query_embedding.tolist(),
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "cached_at": datetime.utcnow().isoformat(),
            "user_id": user_context.get("user_id") if user_context else None
        }
        
        try:
            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
            logger.debug(f"Cached result: {cache_key}")
        except Exception as e:
            logger.warning(f"Error caching result: {e}")
    
    def clear(self, pattern: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match keys (default: all cache keys)
        """
        if pattern is None:
            pattern = "cache:*"
        
        try:
            keys = list(self.redis_client.scan_iter(match=pattern))
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


import asyncio
import json
import time
import logging
import hashlib
import pickle
import gzip
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import weakref

# Google Cloud imports
from google.cloud import firestore
from google.cloud import storage
from google.cloud import monitoring_v3

# Try to import optional dependencies
try:
    from google.cloud import memcache
except ImportError:
    memcache = None

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from ...core.gcp_config import GCPSettings
from ...middleware.monitoring import performance_monitor
from ...core.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheLevel(Enum):
    """Cache levels in order of access speed"""
    L1_MEMORY = 1      # In-memory cache (fastest)
    L2_REDIS = 2       # Distributed Redis cache
    L3_MEMCACHED = 3   # GCP Memorystore Memcached
    L4_PERSISTENT = 4  # Firestore/Storage (slowest)

class CacheStrategy(Enum):
    """Cache storage strategies"""
    WRITE_THROUGH = "write_through"       # Write to cache and storage simultaneously
    WRITE_BACK = "write_back"            # Write to cache, lazy write to storage
    WRITE_AROUND = "write_around"        # Skip cache, write directly to storage
    CACHE_ASIDE = "cache_aside"          # Manual cache management

class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"                          # Least Recently Used
    LFU = "lfu"                          # Least Frequently Used
    TTL = "ttl"                          # Time To Live
    FIFO = "fifo"                        # First In, First Out

@dataclass
class CacheConfig:
    """Configuration for cache levels"""
    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    compression: bool = False
    serialization: str = 'json'  # 'json', 'pickle', 'msgpack'

@dataclass
class CacheItem:
    """Cached item with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = None

@dataclass
class CacheStats:
    """Cache statistics"""
    level: CacheLevel
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_items: int = 0
    memory_usage_bytes: int = 0
    avg_response_time_ms: float = 0.0
    hit_ratio: float = 0.0

class LRUCache(Generic[T]):
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheItem] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[T]:
        async with self._lock:
            if key in self._cache:
                item = self._cache[key]
                
                # Check TTL
                if self._is_expired(item):
                    await self._remove_item(key)
                    return None
                
                # Update access info
                item.last_accessed = datetime.now(timezone.utc)
                item.access_count += 1
                
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                
                return item.value
            
            return None
    
    async def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        async with self._lock:
            now = datetime.now(timezone.utc)
            
            # Calculate item size
            size_bytes = len(json.dumps(value, default=str).encode('utf-8'))
            
            # Create cache item
            item = CacheItem(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds or self.ttl_seconds
            )
            
            # Remove existing item if present
            if key in self._cache:
                await self._remove_item(key)
            
            # Add new item
            self._cache[key] = item
            self._access_order.append(key)
            
            # Evict if necessary
            await self._evict_if_needed()
            
            return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                await self._remove_item(key)
                return True
            return False
    
    async def clear(self):
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def size(self) -> int:
        return len(self._cache)
    
    async def _remove_item(self, key: str):
        """Remove item from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    async def _evict_if_needed(self):
        """Evict items if cache is over capacity"""
        while len(self._cache) > self.max_size:
            if self._access_order:
                # Remove least recently used item
                lru_key = self._access_order[0]
                await self._remove_item(lru_key)
    
    def _is_expired(self, item: CacheItem) -> bool:
        """Check if cache item has expired"""
        if item.ttl_seconds is None:
            return False
        
        age = (datetime.now(timezone.utc) - item.created_at).total_seconds()
        return age > item.ttl_seconds

class MultiLevelCacheManager:
    """
    Multi-level cache manager with L1 (Memory) -> L2 (Redis) -> L3 (Memcached) -> L4 (Persistent)
    """
    
    def __init__(self, project_id: str = None):
        self.settings = GCPSettings() if not project_id else GCPSettings(project_id=project_id)
        
        # Cache configurations by level
        self.cache_configs = {
            CacheLevel.L1_MEMORY: CacheConfig(
                enabled=True,
                max_size=1000,
                ttl_seconds=300,  # 5 minutes
                eviction_policy=EvictionPolicy.LRU,
                compression=False,
                serialization='json'
            ),
            CacheLevel.L2_REDIS: CacheConfig(
                enabled=FeatureFlags.REDIS_CACHE_ENABLED if hasattr(FeatureFlags, 'REDIS_CACHE_ENABLED') else True,
                max_size=10000,
                ttl_seconds=1800,  # 30 minutes
                eviction_policy=EvictionPolicy.LRU,
                compression=True,
                serialization='pickle'
            ),
            CacheLevel.L3_MEMCACHED: CacheConfig(
                enabled=True,
                max_size=50000,
                ttl_seconds=3600,  # 1 hour
                eviction_policy=EvictionPolicy.LRU,
                compression=True,
                serialization='pickle'
            ),
            CacheLevel.L4_PERSISTENT: CacheConfig(
                enabled=True,
                max_size=1000000,
                ttl_seconds=86400,  # 24 hours
                eviction_policy=EvictionPolicy.TTL,
                compression=True,
                serialization='pickle'
            )
        }
        
        # Initialize cache layers
        self.l1_cache = LRUCache(self.cache_configs[CacheLevel.L1_MEMORY].max_size)
        self.redis_client: Optional[redis.Redis] = None
        self.memcached_client: Optional[memcache.Client] = None
        self.firestore_client: Optional[firestore.Client] = None
        self.storage_client: Optional[storage.Client] = None
        
        # Statistics tracking
        self.stats: Dict[CacheLevel, CacheStats] = {
            level: CacheStats(level=level) for level in CacheLevel
        }
        
        # Monitoring
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
        logger.info("✅ Multi-Level Cache Manager initialized")
    
    async def initialize(self):
        """Initialize all cache layers"""
        try:
            # Initialize Redis (L2)
            if self.cache_configs[CacheLevel.L2_REDIS].enabled and redis:
                await self._init_redis()
            elif self.cache_configs[CacheLevel.L2_REDIS].enabled:
                logger.warning("Redis not available - disabling L2 cache")
                self.cache_configs[CacheLevel.L2_REDIS].enabled = False
            
            # Initialize Memcached (L3)
            if self.cache_configs[CacheLevel.L3_MEMCACHED].enabled and memcache:
                await self._init_memcached()
            elif self.cache_configs[CacheLevel.L3_MEMCACHED].enabled:
                logger.warning("Memcached not available - disabling L3 cache")
                self.cache_configs[CacheLevel.L3_MEMCACHED].enabled = False
            
            # Initialize Persistent layer (L4)
            if self.cache_configs[CacheLevel.L4_PERSISTENT].enabled:
                await self._init_persistent()
            
            logger.info("Multi-Level Cache Manager fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = getattr(self.settings, 'redis_host', 'localhost')
            redis_port = getattr(self.settings, 'redis_port', 6379)
            redis_db = getattr(self.settings, 'redis_db', 0)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False,  # Handle binary data
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.cache_configs[CacheLevel.L2_REDIS].enabled = False
    
    async def _init_memcached(self):
        """Initialize Memcached connection"""
        try:
            # For GCP Memorystore Memcached
            memcached_endpoint = getattr(self.settings, 'memcached_endpoint', None)
            
            if memcached_endpoint:
                self.memcached_client = memcache.Client(
                    project=self.settings.project_id,
                    region=self.settings.region
                )
                logger.info("✅ Memcached cache initialized")
            else:
                logger.warning("Memcached endpoint not configured")
                self.cache_configs[CacheLevel.L3_MEMCACHED].enabled = False
                
        except Exception as e:
            logger.error(f"Failed to initialize Memcached: {e}")
            self.cache_configs[CacheLevel.L3_MEMCACHED].enabled = False
    
    async def _init_persistent(self):
        """Initialize persistent storage layer"""
        try:
            self.firestore_client = firestore.Client(project=self.settings.project_id)
            self.storage_client = storage.Client(project=self.settings.project_id)
            
            logger.info("✅ Persistent cache layer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize persistent layer: {e}")
            self.cache_configs[CacheLevel.L4_PERSISTENT].enabled = False
    
    @performance_monitor
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with multi-level lookup
        """
        start_time = time.time()
        
        try:
            # L1 Cache (Memory) - Fastest
            if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
                value = await self._get_from_l1(key)
                if value is not None:
                    await self._record_hit(CacheLevel.L1_MEMORY, time.time() - start_time)
                    return value
                else:
                    await self._record_miss(CacheLevel.L1_MEMORY)
            
            # L2 Cache (Redis) - Fast distributed
            if self.cache_configs[CacheLevel.L2_REDIS].enabled and self.redis_client:
                value = await self._get_from_l2(key)
                if value is not None:
                    # Promote to L1
                    await self._promote_to_l1(key, value)
                    await self._record_hit(CacheLevel.L2_REDIS, time.time() - start_time)
                    return value
                else:
                    await self._record_miss(CacheLevel.L2_REDIS)
            
            # L3 Cache (Memcached) - Medium speed
            if self.cache_configs[CacheLevel.L3_MEMCACHED].enabled and self.memcached_client:
                value = await self._get_from_l3(key)
                if value is not None:
                    # Promote to L2 and L1
                    await self._promote_to_l2(key, value)
                    await self._promote_to_l1(key, value)
                    await self._record_hit(CacheLevel.L3_MEMCACHED, time.time() - start_time)
                    return value
                else:
                    await self._record_miss(CacheLevel.L3_MEMCACHED)
            
            # L4 Cache (Persistent) - Slowest but most reliable
            if self.cache_configs[CacheLevel.L4_PERSISTENT].enabled:
                value = await self._get_from_l4(key)
                if value is not None:
                    # Promote to all upper levels
                    await self._promote_to_l3(key, value)
                    await self._promote_to_l2(key, value)
                    await self._promote_to_l1(key, value)
                    await self._record_hit(CacheLevel.L4_PERSISTENT, time.time() - start_time)
                    return value
                else:
                    await self._record_miss(CacheLevel.L4_PERSISTENT)
            
            return default
            
        except Exception as e:
            logger.error(f"Cache get operation failed for key {key}: {e}")
            return default
    
    @performance_monitor
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, 
                 strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH) -> bool:
        """
        Set value in cache with specified strategy
        """
        try:
            success = True
            
            if strategy == CacheStrategy.WRITE_THROUGH:
                # Write to all levels simultaneously
                tasks = []
                
                if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
                    tasks.append(self._set_in_l1(key, value, ttl_seconds))
                
                if self.cache_configs[CacheLevel.L2_REDIS].enabled and self.redis_client:
                    tasks.append(self._set_in_l2(key, value, ttl_seconds))
                
                if self.cache_configs[CacheLevel.L3_MEMCACHED].enabled and self.memcached_client:
                    tasks.append(self._set_in_l3(key, value, ttl_seconds))
                
                if self.cache_configs[CacheLevel.L4_PERSISTENT].enabled:
                    tasks.append(self._set_in_l4(key, value, ttl_seconds))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success = all(r is True or not isinstance(r, Exception) for r in results)
                
            elif strategy == CacheStrategy.CACHE_ASIDE:
                # Only write to L1 (manual management)
                if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
                    success = await self._set_in_l1(key, value, ttl_seconds)
            
            # Record statistics
            for level in CacheLevel:
                if self.cache_configs[level].enabled:
                    self.stats[level].sets += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set operation failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete from all cache levels"""
        try:
            tasks = []
            
            if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
                tasks.append(self._delete_from_l1(key))
            
            if self.cache_configs[CacheLevel.L2_REDIS].enabled and self.redis_client:
                tasks.append(self._delete_from_l2(key))
            
            if self.cache_configs[CacheLevel.L3_MEMCACHED].enabled and self.memcached_client:
                tasks.append(self._delete_from_l3(key))
            
            if self.cache_configs[CacheLevel.L4_PERSISTENT].enabled:
                tasks.append(self._delete_from_l4(key))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success = any(r is True for r in results)
            
            # Record statistics
            if success:
                for level in CacheLevel:
                    if self.cache_configs[level].enabled:
                        self.stats[level].deletes += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete operation failed for key {key}: {e}")
            return False
    
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        invalidated_count = 0
        
        try:
            # L1 - scan in-memory keys
            if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
                l1_keys = []
                async with self.l1_cache._lock:
                    for key in self.l1_cache._cache.keys():
                        if self._match_pattern(key, pattern):
                            l1_keys.append(key)
                
                for key in l1_keys:
                    await self.l1_cache.delete(key)
                    invalidated_count += 1
            
            # L2 - Redis pattern scan
            if self.cache_configs[CacheLevel.L2_REDIS].enabled and self.redis_client:
                async for key in self.redis_client.scan_iter(match=pattern):
                    await self.redis_client.delete(key)
                    invalidated_count += 1
            
            # L3 & L4 - more complex pattern matching needed
            # For now, we'll skip these layers for pattern invalidation
            
            logger.info(f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Cache invalidation failed for pattern {pattern}: {e}")
            return 0
    
    # L1 Cache Operations (Memory)
    async def _get_from_l1(self, key: str) -> Any:
        """Get from L1 memory cache"""
        return await self.l1_cache.get(key)
    
    async def _set_in_l1(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set in L1 memory cache"""
        return await self.l1_cache.set(key, value, ttl_seconds)
    
    async def _delete_from_l1(self, key: str) -> bool:
        """Delete from L1 memory cache"""
        return await self.l1_cache.delete(key)
    
    async def _promote_to_l1(self, key: str, value: Any):
        """Promote value to L1 cache"""
        try:
            await self._set_in_l1(key, value)
        except Exception as e:
            logger.debug(f"Failed to promote to L1: {e}")
    
    # L2 Cache Operations (Redis)
    async def _get_from_l2(self, key: str) -> Any:
        """Get from L2 Redis cache"""
        try:
            if not self.redis_client:
                return None
            
            data = await self.redis_client.get(key)
            if data:
                # Deserialize based on configuration
                config = self.cache_configs[CacheLevel.L2_REDIS]
                if config.compression:
                    data = gzip.decompress(data)
                
                if config.serialization == 'pickle':
                    return pickle.loads(data)
                elif config.serialization == 'json':
                    return json.loads(data.decode('utf-8'))
                
            return None
            
        except Exception as e:
            logger.debug(f"L2 cache get failed: {e}")
            return None
    
    async def _set_in_l2(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set in L2 Redis cache"""
        try:
            if not self.redis_client:
                return False
            
            config = self.cache_configs[CacheLevel.L2_REDIS]
            
            # Serialize based on configuration
            if config.serialization == 'pickle':
                data = pickle.dumps(value)
            elif config.serialization == 'json':
                data = json.dumps(value, default=str).encode('utf-8')
            else:
                data = str(value).encode('utf-8')
            
            # Compress if enabled
            if config.compression:
                data = gzip.compress(data)
            
            # Set with TTL
            ttl = ttl_seconds or config.ttl_seconds
            success = await self.redis_client.setex(key, ttl, data)
            
            return success is True
            
        except Exception as e:
            logger.debug(f"L2 cache set failed: {e}")
            return False
    
    async def _delete_from_l2(self, key: str) -> bool:
        """Delete from L2 Redis cache"""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.debug(f"L2 cache delete failed: {e}")
            return False
    
    async def _promote_to_l2(self, key: str, value: Any):
        """Promote value to L2 cache"""
        try:
            await self._set_in_l2(key, value)
        except Exception as e:
            logger.debug(f"Failed to promote to L2: {e}")
    
    # L3 Cache Operations (Memcached) - Simplified implementation
    async def _get_from_l3(self, key: str) -> Any:
        """Get from L3 Memcached cache"""
        # Placeholder for GCP Memorystore Memcached implementation
        return None
    
    async def _set_in_l3(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set in L3 Memcached cache"""
        # Placeholder for GCP Memorystore Memcached implementation
        return False
    
    async def _delete_from_l3(self, key: str) -> bool:
        """Delete from L3 Memcached cache"""
        # Placeholder for GCP Memorystore Memcached implementation
        return False
    
    async def _promote_to_l3(self, key: str, value: Any):
        """Promote value to L3 cache"""
        try:
            await self._set_in_l3(key, value)
        except Exception as e:
            logger.debug(f"Failed to promote to L3: {e}")
    
    # L4 Cache Operations (Persistent Storage)
    async def _get_from_l4(self, key: str) -> Any:
        """Get from L4 persistent cache"""
        try:
            if not self.firestore_client:
                return None
            
            # Use Firestore for structured data caching
            doc_ref = self.firestore_client.collection('cache_l4').document(
                hashlib.md5(key.encode()).hexdigest()
            )
            
            doc = await asyncio.get_event_loop().run_in_executor(None, doc_ref.get)
            
            if doc.exists:
                data = doc.to_dict()
                
                # Check expiration
                created_at = data.get('created_at')
                ttl_seconds = data.get('ttl_seconds')
                
                if created_at and ttl_seconds:
                    age = (datetime.now(timezone.utc) - created_at).total_seconds()
                    if age > ttl_seconds:
                        # Expired, delete and return None
                        await asyncio.get_event_loop().run_in_executor(None, doc_ref.delete)
                        return None
                
                # Deserialize value
                serialized_value = data.get('value')
                if serialized_value:
                    config = self.cache_configs[CacheLevel.L4_PERSISTENT]
                    
                    if config.serialization == 'pickle':
                        return pickle.loads(serialized_value.encode('latin-1'))
                    elif config.serialization == 'json':
                        return json.loads(serialized_value)
            
            return None
            
        except Exception as e:
            logger.debug(f"L4 cache get failed: {e}")
            return None
    
    async def _set_in_l4(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set in L4 persistent cache"""
        try:
            if not self.firestore_client:
                return False
            
            config = self.cache_configs[CacheLevel.L4_PERSISTENT]
            
            # Serialize value
            if config.serialization == 'pickle':
                serialized_value = pickle.dumps(value).decode('latin-1')
            elif config.serialization == 'json':
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            # Prepare document
            doc_data = {
                'key': key,
                'value': serialized_value,
                'created_at': datetime.now(timezone.utc),
                'ttl_seconds': ttl_seconds or config.ttl_seconds,
                'serialization': config.serialization
            }
            
            # Store in Firestore
            doc_ref = self.firestore_client.collection('cache_l4').document(
                hashlib.md5(key.encode()).hexdigest()
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, doc_ref.set, doc_data
            )
            
            return True
            
        except Exception as e:
            logger.debug(f"L4 cache set failed: {e}")
            return False
    
    async def _delete_from_l4(self, key: str) -> bool:
        """Delete from L4 persistent cache"""
        try:
            if not self.firestore_client:
                return False
            
            doc_ref = self.firestore_client.collection('cache_l4').document(
                hashlib.md5(key.encode()).hexdigest()
            )
            
            await asyncio.get_event_loop().run_in_executor(None, doc_ref.delete)
            return True
            
        except Exception as e:
            logger.debug(f"L4 cache delete failed: {e}")
            return False
    
    # Statistics and monitoring
    async def _record_hit(self, level: CacheLevel, response_time: float):
        """Record cache hit statistics"""
        stats = self.stats[level]
        stats.hits += 1
        
        # Update average response time
        total_ops = stats.hits + stats.misses
        stats.avg_response_time_ms = (
            (stats.avg_response_time_ms * (total_ops - 1) + response_time * 1000) / total_ops
        )
        
        stats.hit_ratio = stats.hits / max(1, stats.hits + stats.misses)
        
        # Record to GCP Monitoring
        await self._record_gcp_cache_metrics(level, 'hit', response_time)
    
    async def _record_miss(self, level: CacheLevel):
        """Record cache miss statistics"""
        stats = self.stats[level]
        stats.misses += 1
        stats.hit_ratio = stats.hits / max(1, stats.hits + stats.misses)
        
        # Record to GCP Monitoring
        await self._record_gcp_cache_metrics(level, 'miss', 0)
    
    async def _record_gcp_cache_metrics(self, level: CacheLevel, operation: str, response_time: float):
        """Record cache metrics to GCP Monitoring"""
        try:
            project_name = f"projects/{self.settings.project_id}"
            
            # Cache operation metric
            series = monitoring_v3.TimeSeries()
            series.metric.type = "custom.googleapis.com/validatus/cache_operations"
            series.resource.type = "global"
            series.metric.labels['cache_level'] = level.name
            series.metric.labels['operation'] = operation
            
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"int64_value": 1}
            })
            series.points = [point]
            
            # Response time metric (for hits)
            response_series = None
            if operation == 'hit':
                response_series = monitoring_v3.TimeSeries()
                response_series.metric.type = "custom.googleapis.com/validatus/cache_response_time"
                response_series.resource.type = "global"
                response_series.metric.labels['cache_level'] = level.name
                
                response_point = monitoring_v3.Point({
                    "interval": interval,
                    "value": {"double_value": response_time * 1000}  # Convert to milliseconds
                })
                response_series.points = [response_point]
            
            # Send metrics
            time_series = [series]
            if response_series:
                time_series.append(response_series)
            
            self.monitoring_client.create_time_series(
                name=project_name, 
                time_series=time_series
            )
            
        except Exception as e:
            logger.debug(f"Failed to record cache metrics: {e}")
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for cache invalidation"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        
        stats_summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'levels': {},
            'overall': {
                'total_hits': 0,
                'total_misses': 0,
                'total_operations': 0,
                'overall_hit_ratio': 0.0
            }
        }
        
        total_hits = 0
        total_misses = 0
        
        for level, stats in self.stats.items():
            if self.cache_configs[level].enabled:
                level_stats = {
                    'enabled': True,
                    'hits': stats.hits,
                    'misses': stats.misses,
                    'sets': stats.sets,
                    'deletes': stats.deletes,
                    'hit_ratio': stats.hit_ratio,
                    'avg_response_time_ms': stats.avg_response_time_ms,
                    'total_items': await self._get_level_item_count(level)
                }
                
                stats_summary['levels'][level.name] = level_stats
                total_hits += stats.hits
                total_misses += stats.misses
        
        # Overall statistics
        total_ops = total_hits + total_misses
        if total_ops > 0:
            stats_summary['overall']['total_hits'] = total_hits
            stats_summary['overall']['total_misses'] = total_misses
            stats_summary['overall']['total_operations'] = total_ops
            stats_summary['overall']['overall_hit_ratio'] = total_hits / total_ops
        
        return stats_summary
    
    async def _get_level_item_count(self, level: CacheLevel) -> int:
        """Get current item count for a cache level"""
        try:
            if level == CacheLevel.L1_MEMORY:
                return await self.l1_cache.size()
            elif level == CacheLevel.L2_REDIS and self.redis_client:
                return await self.redis_client.dbsize()
            else:
                return 0  # Placeholder for other levels
        except:
            return 0
    
    async def clear_all_caches(self):
        """Clear all cache levels"""
        tasks = []
        
        if self.cache_configs[CacheLevel.L1_MEMORY].enabled:
            tasks.append(self.l1_cache.clear())
        
        if self.cache_configs[CacheLevel.L2_REDIS].enabled and self.redis_client:
            tasks.append(self.redis_client.flushdb())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("All cache levels cleared")
    
    async def shutdown(self):
        """Gracefully shutdown cache manager"""
        logger.info("Shutting down Multi-Level Cache Manager...")
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Clear memory cache
        await self.l1_cache.clear()
        
        logger.info("Multi-Level Cache Manager shutdown completed")

__all__ = [
    'MultiLevelCacheManager', 'CacheLevel', 'CacheStrategy', 
    'CacheConfig', 'CacheStats', 'EvictionPolicy'
]

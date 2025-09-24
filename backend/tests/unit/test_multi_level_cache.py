"""
Unit tests for Phase E Multi-Level Cache Manager component.

Tests L1-L4 caching, cache policies, and cache performance optimization.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from app.services.enhanced_orchestration.multi_level_cache_manager import (
    MultiLevelCacheManager,
    CacheLevel,
    CacheConfig,
    CacheItem,
    CacheStats
)


@pytest.mark.unit
@pytest.mark.phase_e
class TestMultiLevelCacheManager:
    """Test suite for Multi-Level Cache Manager."""

    @pytest.fixture
    async def cache_manager(self, mock_gcp_settings, mock_feature_flags):
        """Create a test cache manager instance."""
        with patch('app.services.enhanced_orchestration.multi_level_cache_manager.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            cache_manager = MultiLevelCacheManager(
                project_id="test-project",
                cache_config=CacheConfig(
                    l1_max_size=100,
                    l1_ttl=300,
                    l2_ttl=600,
                    l3_ttl=1800,
                    l4_ttl=3600
                )
            )
            
            # Mock Redis and Memcached
            cache_manager._redis_client = AsyncMock()
            cache_manager._memcached_client = AsyncMock()
            cache_manager._firestore_client = Mock()
            cache_manager._storage_client = Mock()
            
            await cache_manager.initialize()
            return cache_manager

    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self, mock_gcp_settings):
        """Test cache manager initialization."""
        with patch('app.services.enhanced_orchestration.multi_level_cache_manager.GCPSettings') as mock_settings:
            mock_settings.return_value = mock_gcp_settings
            
            cache_manager = MultiLevelCacheManager(project_id="test-project")
            
            assert cache_manager.project_id == "test-project"
            assert cache_manager.config.l1_max_size == 1000
            assert cache_manager.config.l1_ttl == 300
            assert cache_manager.stats.total_requests == 0
            assert cache_manager.stats.total_hits == 0

    @pytest.mark.asyncio
    async def test_l1_cache_operations(self, cache_manager):
        """Test L1 (in-memory) cache operations."""
        key = "test_key"
        value = {"data": "test_value", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        # Test set operation
        await cache_manager.set(key, value)
        
        # Verify item is in L1 cache
        assert key in cache_manager._l1_cache
        cache_item = cache_manager._l1_cache[key]
        assert cache_item.value == value
        assert cache_item.level == CacheLevel.L1
        assert cache_item.access_count == 0
        
        # Test get operation
        result = await cache_manager.get(key)
        assert result == value
        
        # Verify access count increased
        assert cache_manager._l1_cache[key].access_count == 1

    @pytest.mark.asyncio
    async def test_cache_hit_miss_tracking(self, cache_manager):
        """Test cache hit/miss tracking."""
        # Test miss
        result = await cache_manager.get("nonexistent_key")
        assert result is None
        assert cache_manager.stats.total_requests == 1
        assert cache_manager.stats.total_misses == 1
        assert cache_manager.stats.total_hits == 0
        
        # Test hit
        await cache_manager.set("test_key", "test_value")
        result = await cache_manager.get("test_key")
        assert result == "test_value"
        assert cache_manager.stats.total_requests == 2
        assert cache_manager.stats.total_hits == 1
        assert cache_manager.stats.total_misses == 1

    @pytest.mark.asyncio
    async def test_cache_level_promotion(self, cache_manager):
        """Test cache level promotion based on access patterns."""
        key = "hot_key"
        value = "hot_value"
        
        # Set item in L1
        await cache_manager.set(key, value)
        
        # Simulate high access count
        for _ in range(10):
            await cache_manager.get(key)
        
        # Verify access count
        assert cache_manager._l1_cache[key].access_count == 10
        
        # Manually trigger promotion (normally done by maintenance task)
        await cache_manager._promote_hot_items()
        
        # Item should still be in L1 but marked for promotion
        assert key in cache_manager._l1_cache

    @pytest.mark.asyncio
    async def test_cache_eviction_policies(self, cache_manager):
        """Test cache eviction policies."""
        # Fill L1 cache beyond capacity
        cache_manager.config.l1_max_size = 5
        
        # Add items to fill cache
        for i in range(7):  # Exceed capacity
            await cache_manager.set(f"key_{i}", f"value_{i}")
        
        # Verify cache size doesn't exceed capacity
        assert len(cache_manager._l1_cache) <= cache_manager.config.l1_max_size

    @pytest.mark.asyncio
    async def test_l2_redis_operations(self, cache_manager):
        """Test L2 (Redis) cache operations."""
        # Mock Redis operations
        cache_manager._redis_client.get = AsyncMock(return_value=None)
        cache_manager._redis_client.setex = AsyncMock(return_value=True)
        
        key = "redis_test_key"
        value = {"data": "redis_value"}
        
        # Test set operation
        await cache_manager._set_l2(key, value)
        cache_manager._redis_client.setex.assert_called_once()
        
        # Test get operation
        cache_manager._redis_client.get = AsyncMock(return_value=b'{"data": "redis_value"}')
        result = await cache_manager._get_l2(key)
        assert result == value

    @pytest.mark.asyncio
    async def test_l3_memcached_operations(self, cache_manager):
        """Test L3 (Memcached) cache operations."""
        # Mock Memcached operations
        cache_manager._memcached_client.get = AsyncMock(return_value=None)
        cache_manager._memcached_client.set = AsyncMock(return_value=True)
        
        key = "memcached_test_key"
        value = {"data": "memcached_value"}
        
        # Test set operation
        await cache_manager._set_l3(key, value)
        cache_manager._memcached_client.set.assert_called_once()
        
        # Test get operation
        cache_manager._memcached_client.get = AsyncMock(return_value=b'{"data": "memcached_value"}')
        result = await cache_manager._get_l3(key)
        assert result == value

    @pytest.mark.asyncio
    async def test_l4_persistent_operations(self, cache_manager):
        """Test L4 (Firestore/Storage) cache operations."""
        # Mock Firestore operations
        mock_doc = Mock()
        mock_doc.get = Mock(return_value={"value": {"data": "persistent_value"}})
        cache_manager._firestore_client.collection.return_value.document.return_value = mock_doc
        
        key = "persistent_test_key"
        value = {"data": "persistent_value"}
        
        # Test set operation
        await cache_manager._set_l4(key, value)
        
        # Test get operation
        result = await cache_manager._get_l4(key)
        assert result == {"data": "persistent_value"}

    @pytest.mark.asyncio
    async def test_cache_serialization_compression(self, cache_manager):
        """Test cache serialization and compression."""
        # Test with large data
        large_data = {
            "large_array": list(range(10000)),
            "nested_data": {
                "level1": {
                    "level2": {
                        "level3": "deep_value"
                    }
                }
            }
        }
        
        key = "large_data_key"
        
        # Set large data
        await cache_manager.set(key, large_data)
        
        # Retrieve and verify
        result = await cache_manager.get(key)
        assert result == large_data

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, cache_manager):
        """Test cache invalidation operations."""
        # Set items in different cache levels
        await cache_manager.set("l1_key", "l1_value")
        await cache_manager.set("l2_key", "l2_value")
        
        # Mock Redis and Memcached delete operations
        cache_manager._redis_client.delete = AsyncMock(return_value=1)
        cache_manager._memcached_client.delete = AsyncMock(return_value=True)
        
        # Test single key invalidation
        await cache_manager.invalidate("l1_key")
        assert "l1_key" not in cache_manager._l1_cache
        
        # Test pattern-based invalidation
        await cache_manager.invalidate_pattern("l2_*")
        cache_manager._redis_client.delete.assert_called()

    @pytest.mark.asyncio
    async def test_cache_statistics(self, cache_manager):
        """Test cache statistics tracking."""
        # Perform various operations
        await cache_manager.set("key1", "value1")
        await cache_manager.get("key1")  # Hit
        await cache_manager.get("key2")  # Miss
        await cache_manager.set("key3", "value3")
        await cache_manager.get("key3")  # Hit
        
        stats = cache_manager.get_cache_stats()
        
        assert stats.total_requests == 3
        assert stats.total_hits == 2
        assert stats.total_misses == 1
        assert stats.hit_rate == 2/3
        assert stats.l1_size == 2  # Two items in L1
        assert stats.l1_hit_rate >= 0
        assert stats.l2_hit_rate >= 0
        assert stats.l3_hit_rate >= 0
        assert stats.l4_hit_rate >= 0

    @pytest.mark.asyncio
    async def test_cache_warming(self, cache_manager):
        """Test cache warming functionality."""
        # Mock data source
        data_source = AsyncMock()
        data_source.get_data = AsyncMock(return_value=[
            ("warm_key1", {"data": "warm_value1"}),
            ("warm_key2", {"data": "warm_value2"}),
            ("warm_key3", {"data": "warm_value3"})
        ])
        
        # Warm cache
        await cache_manager.warm_cache(data_source.get_data)
        
        # Verify items are in cache
        assert await cache_manager.get("warm_key1") == {"data": "warm_value1"}
        assert await cache_manager.get("warm_key2") == {"data": "warm_value2"}
        assert await cache_manager.get("warm_key3") == {"data": "warm_value3"}

    @pytest.mark.asyncio
    async def test_cache_health_monitoring(self, cache_manager):
        """Test cache health monitoring."""
        # Mock Redis health check
        cache_manager._redis_client.ping = AsyncMock(return_value=True)
        
        # Mock Memcached health check
        cache_manager._memcached_client.get = AsyncMock(return_value=None)
        
        health = await cache_manager.get_cache_health()
        
        assert 'timestamp' in health
        assert 'l1_status' in health
        assert 'l2_status' in health
        assert 'l3_status' in health
        assert 'l4_status' in health
        assert 'overall_status' in health
        
        assert health['l1_status'] == 'healthy'
        assert health['l2_status'] in ['healthy', 'unavailable']
        assert health['l3_status'] in ['healthy', 'unavailable']
        assert health['l4_status'] in ['healthy', 'unavailable']

    @pytest.mark.asyncio
    async def test_cache_maintenance_tasks(self, cache_manager):
        """Test cache maintenance tasks."""
        # Add some test data
        await cache_manager.set("test_key", "test_value")
        
        # Run maintenance tasks
        await cache_manager._cleanup_expired_items()
        await cache_manager._update_statistics()
        
        # Verify statistics are updated
        assert cache_manager.stats.last_updated is not None

    @pytest.mark.asyncio
    async def test_cache_manager_shutdown(self, cache_manager):
        """Test cache manager graceful shutdown."""
        # Verify maintenance tasks are running
        assert len(cache_manager._maintenance_tasks) > 0
        
        # Shutdown cache manager
        await cache_manager.shutdown()
        
        # Check that tasks are cancelled
        for task in cache_manager._maintenance_tasks:
            assert task.done() or task.cancelled()


@pytest.mark.unit
@pytest.mark.phase_e
class TestCacheConfig:
    """Test suite for Cache Configuration."""

    def test_default_config(self):
        """Test default cache configuration."""
        config = CacheConfig()
        
        assert config.l1_max_size == 1000
        assert config.l1_ttl == 300
        assert config.l2_ttl == 600
        assert config.l3_ttl == 1800
        assert config.l4_ttl == 3600
        assert config.compression_enabled is True
        assert config.serialization_format == 'msgpack'

    def test_custom_config(self):
        """Test custom cache configuration."""
        config = CacheConfig(
            l1_max_size=500,
            l1_ttl=600,
            l2_ttl=1200,
            l3_ttl=3600,
            l4_ttl=7200,
            compression_enabled=False,
            serialization_format='json'
        )
        
        assert config.l1_max_size == 500
        assert config.l1_ttl == 600
        assert config.l2_ttl == 1200
        assert config.l3_ttl == 3600
        assert config.l4_ttl == 7200
        assert config.compression_enabled is False
        assert config.serialization_format == 'json'


@pytest.mark.unit
@pytest.mark.phase_e
class TestCacheItem:
    """Test suite for Cache Item."""

    def test_cache_item_creation(self):
        """Test cache item creation."""
        value = {"data": "test"}
        item = CacheItem(
            key="test_key",
            value=value,
            level=CacheLevel.L1,
            ttl=300
        )
        
        assert item.key == "test_key"
        assert item.value == value
        assert item.level == CacheLevel.L1
        assert item.ttl == 300
        assert item.created_at is not None
        assert item.access_count == 0

    def test_cache_item_expiry(self):
        """Test cache item expiry calculation."""
        item = CacheItem(
            key="test_key",
            value="test_value",
            level=CacheLevel.L1,
            ttl=300
        )
        
        # Item should not be expired immediately
        assert not item.is_expired()
        
        # Manually set old creation time
        item.created_at = datetime.now(timezone.utc) - timedelta(seconds=400)
        
        # Item should be expired now
        assert item.is_expired()


@pytest.mark.unit
@pytest.mark.phase_e
class TestCacheStats:
    """Test suite for Cache Statistics."""

    def test_stats_creation(self):
        """Test cache statistics creation."""
        stats = CacheStats()
        
        assert stats.total_requests == 0
        assert stats.total_hits == 0
        assert stats.total_misses == 0
        assert stats.hit_rate == 0.0
        assert stats.l1_hits == 0
        assert stats.l2_hits == 0
        assert stats.l3_hits == 0
        assert stats.l4_hits == 0
        assert stats.last_updated is not None

    def test_stats_calculation(self):
        """Test cache statistics calculation."""
        stats = CacheStats()
        
        # Update stats
        stats.total_requests = 100
        stats.total_hits = 80
        stats.total_misses = 20
        stats.l1_hits = 60
        stats.l2_hits = 15
        stats.l3_hits = 5
        stats.l4_hits = 0
        
        # Calculate hit rate
        stats.hit_rate = stats.total_hits / stats.total_requests
        
        assert stats.hit_rate == 0.8
        assert stats.total_requests == 100
        assert stats.total_hits == 80
        assert stats.total_misses == 20

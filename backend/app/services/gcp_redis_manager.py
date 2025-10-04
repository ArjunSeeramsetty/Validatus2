"""
Google Memorystore Redis Manager
Handles caching, session management, and real-time data operations
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

class GCPRedisManager:
    """Manages Google Memorystore Redis operations"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Redis connection pool"""
        if self._initialized:
            return
        
        try:
            if self.settings.local_development_mode:
                redis_url = self.settings.local_redis_url
            else:
                redis_url = f"redis://{self.settings.redis_host}:{self.settings.redis_port}/0"
                if self.settings.redis_password:
                    redis_url = f"redis://:{self.settings.redis_password}@{self.settings.redis_host}:{self.settings.redis_port}/0"
            
            self.pool = ConnectionPool.from_url(
                redis_url,
                max_connections=self.settings.connection_pool_size,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            self.client = Redis(connection_pool=self.pool, decode_responses=True)
            
            # Test connection
            await self.client.ping()
            
            self._initialized = True
            logger.info("Redis connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            raise
    
    async def close(self):
        """Close Redis connection pool"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False
        logger.info("Redis connection pool closed")
    
    async def _ensure_initialized(self):
        """Ensure Redis is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def _ensure_json_serializable(self, data: Any) -> Any:
        """Convert data to JSON-serializable format"""
        if isinstance(data, dict):
            return {key: self._ensure_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._ensure_json_serializable(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif hasattr(data, 'isoformat'):  # datetime objects
            return data.isoformat()
        elif hasattr(data, '__dict__'):  # custom objects
            return self._ensure_json_serializable(data.__dict__)
        else:
            # For unknown types, raise TypeError to surface serialization issues
            raise TypeError(f"Object of type {type(data)} is not JSON serializable")
    
    # Session Management
    async def cache_session_data(self, session_id: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache session data with TTL"""
        await self._ensure_initialized()
        
        try:
            key = f"session:{session_id}"
            # Ensure data is JSON-serializable before calling json.dumps
            serializable_data = self._ensure_json_serializable(data)
            await self.client.setex(key, ttl, json.dumps(serializable_data))
            logger.debug(f"Cached session data for {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache session data for {session_id}: {e}")
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from cache"""
        await self._ensure_initialized()
        
        try:
            key = f"session:{session_id}"
            data = await self.client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session data for {session_id}: {e}")
            return None
    
    async def extend_session_ttl(self, session_id: str, ttl: int = 3600):
        """Extend session TTL"""
        await self._ensure_initialized()
        
        try:
            key = f"session:{session_id}"
            await self.client.expire(key, ttl)
            
        except Exception as e:
            logger.error(f"Failed to extend session TTL for {session_id}: {e}")
    
    # Workflow Progress Caching
    async def cache_workflow_progress(self, session_id: str, stage: str, 
                                    progress_data: Dict[str, Any]):
        """Cache real-time workflow progress"""
        await self._ensure_initialized()
        
        try:
            key = f"workflow:{session_id}"
            
            # Use hash for structured data
            await self.client.hset(key, mapping={
                "current_stage": stage,
                "progress_data": json.dumps(progress_data, default=str),
                "last_updated": datetime.utcnow().isoformat(),
                "progress_percentage": str(progress_data.get('percentage', 0))
            })
            
            # Set TTL for workflow progress (2 hours)
            await self.client.expire(key, 7200)
            
            # Also publish to subscribers for real-time updates
            await self.publish_workflow_update(session_id, stage, progress_data)
            
            logger.debug(f"Cached workflow progress for {session_id}: {stage}")
            
        except Exception as e:
            logger.error(f"Failed to cache workflow progress for {session_id}: {e}")
    
    async def get_workflow_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow progress"""
        await self._ensure_initialized()
        
        try:
            key = f"workflow:{session_id}"
            data = await self.client.hgetall(key)
            
            if data:
                # Parse JSON fields
                if 'progress_data' in data:
                    data['progress_data'] = json.loads(data['progress_data'])
                
                return data
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow progress for {session_id}: {e}")
            return None
    
    # URL Processing Queue
    async def queue_urls_for_processing(self, session_id: str, urls: List[str]):
        """Queue URLs for asynchronous processing"""
        await self._ensure_initialized()
        
        try:
            queue_key = f"queue:scraping:{session_id}"
            
            # Add URLs to queue (left push for FIFO with right pop)
            if urls:
                await self.client.lpush(queue_key, *urls)
                
                # Set TTL for queue (24 hours)
                await self.client.expire(queue_key, 86400)
                
                logger.info(f"Queued {len(urls)} URLs for processing: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to queue URLs for {session_id}: {e}")
    
    async def get_next_url_to_process(self, session_id: str) -> Optional[str]:
        """Get next URL to process from queue"""
        await self._ensure_initialized()
        
        try:
            queue_key = f"queue:scraping:{session_id}"
            url = await self.client.rpop(queue_key)
            
            if url:
                logger.debug(f"Retrieved URL for processing: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to get next URL for {session_id}: {e}")
            return None
    
    async def get_queue_length(self, session_id: str) -> int:
        """Get number of URLs remaining in processing queue"""
        await self._ensure_initialized()
        
        try:
            queue_key = f"queue:scraping:{session_id}"
            length = await self.client.llen(queue_key)
            return length
            
        except Exception as e:
            logger.error(f"Failed to get queue length for {session_id}: {e}")
            return 0
    
    # Analysis Results Caching
    async def cache_analysis_preview(self, session_id: str, analysis_id: str, 
                                   preview_data: Dict[str, Any], ttl: int = 1800):
        """Cache analysis preview results for quick access"""
        await self._ensure_initialized()
        
        try:
            key = f"analysis_preview:{session_id}:{analysis_id}"
            await self.client.setex(key, ttl, json.dumps(preview_data, default=str))
            
            logger.debug(f"Cached analysis preview: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache analysis preview {analysis_id}: {e}")
    
    async def get_analysis_preview(self, session_id: str, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis preview"""
        await self._ensure_initialized()
        
        try:
            key = f"analysis_preview:{session_id}:{analysis_id}"
            data = await self.client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get analysis preview {analysis_id}: {e}")
            return None
    
    # User Activity Tracking
    async def track_user_activity(self, user_id: str, activity_type: str, 
                                activity_data: Dict[str, Any]):
        """Track user activity for analytics"""
        await self._ensure_initialized()
        
        try:
            # Store in sorted set with timestamp score for time-based queries
            key = f"user_activity:{user_id}"
            timestamp = datetime.utcnow().timestamp()
            
            activity_record = {
                'type': activity_type,
                'data': activity_data,
                'timestamp': timestamp
            }
            
            await self.client.zadd(key, {json.dumps(activity_record, default=str): timestamp})
            
            # Keep only last 1000 activities per user
            await self.client.zremrangebyrank(key, 0, -1001)
            
            # Set TTL for user activity (30 days)
            await self.client.expire(key, 2592000)
            
        except Exception as e:
            logger.error(f"Failed to track user activity for {user_id}: {e}")
    
    async def get_recent_user_activity(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        await self._ensure_initialized()
        
        try:
            key = f"user_activity:{user_id}"
            
            # Get activities from last N hours
            since_timestamp = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
            
            activities = await self.client.zrangebyscore(
                key, since_timestamp, '+inf', withscores=True
            )
            
            result = []
            for activity_json, score in activities:
                try:
                    activity = json.loads(activity_json)
                    result.append(activity)
                except json.JSONDecodeError:
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user activity for {user_id}: {e}")
            return []
    
    # Real-time Pub/Sub for UI Updates
    async def publish_workflow_update(self, session_id: str, stage: str, progress_data: Dict[str, Any]):
        """Publish workflow update for real-time UI updates"""
        await self._ensure_initialized()
        
        try:
            channel = f"workflow_updates:{session_id}"
            
            update_message = {
                'session_id': session_id,
                'stage': stage,
                'progress_data': progress_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.client.publish(channel, json.dumps(update_message, default=str))
            
        except Exception as e:
            logger.error(f"Failed to publish workflow update for {session_id}: {e}")
    
    async def subscribe_to_workflow_updates(self, session_id: str):
        """Subscribe to workflow updates for a session"""
        await self._ensure_initialized()
        
        try:
            channel = f"workflow_updates:{session_id}"
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)
            
            return pubsub
            
        except Exception as e:
            logger.error(f"Failed to subscribe to workflow updates for {session_id}: {e}")
            return None
    
    # Rate Limiting
    async def check_rate_limit(self, user_id: str, action: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check if user is within rate limit for an action using atomic Lua script"""
        await self._ensure_initialized()
        
        try:
            key = f"rate_limit:{user_id}:{action}"
            current_time = datetime.utcnow().timestamp()
            window_start = current_time - window_seconds
            member = f"{current_time}:{user_id}"  # Unique member
            
            # Atomic Lua script for rate limiting
            lua_script = """
            local key = KEYS[1]
            local window_start = tonumber(ARGV[1])
            local current_time = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])
            local member = ARGV[4]
            local window_seconds = tonumber(ARGV[5])
            
            -- Remove old entries
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
            
            -- Get current count
            local count = redis.call('ZCARD', key)
            
            if count < limit then
                -- Add current request
                redis.call('ZADD', key, current_time, member)
                redis.call('EXPIRE', key, window_seconds)
                return 1
            else
                return 0
            end
            """
            
            result = await self.client.eval(
                lua_script,
                1,  # number of keys
                key,
                window_start,
                current_time,
                limit,
                member,
                window_seconds
            )
            
            return bool(result)
            
        except Exception as e:
            logger.exception(f"Failed to check rate limit for {user_id}:{action}")
            return True  # Allow on error
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform Redis health check"""
        await self._ensure_initialized()
        
        try:
            start_time = datetime.utcnow()
            
            # Test basic operations
            test_key = "health_check"
            await self.client.set(test_key, "ok", ex=10)
            value = await self.client.get(test_key)
            await self.client.delete(test_key)
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            # Get Redis info
            info = await self.client.info()
            
            return {
                'status': 'healthy' if value == 'ok' else 'unhealthy',
                'response_time_ms': response_time,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'redis_version': info.get('redis_version', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

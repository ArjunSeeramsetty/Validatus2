"""
Google Cloud Storage Manager
Handles all blob storage operations for scraped content, embeddings, and reports
"""
import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, BinaryIO
from urllib.parse import urlparse
import aiofiles

from google.cloud import storage
from google.cloud.storage import Blob, Bucket
from google.api_core import exceptions

from ..core.gcp_persistence_config import get_gcp_persistence_settings

logger = logging.getLogger(__name__)

class GCPStorageManager:
    """Manages Google Cloud Storage operations for Validatus platform"""
    
    def __init__(self):
        self.settings = get_gcp_persistence_settings()
        self.client = storage.Client(project=self.settings.project_id)
        
        # Initialize buckets
        self.content_bucket = self._get_or_create_bucket(self.settings.content_storage_bucket)
        self.embeddings_bucket = self._get_or_create_bucket(self.settings.embeddings_storage_bucket)
        self.reports_bucket = self._get_or_create_bucket(self.settings.reports_storage_bucket)
        
        logger.info("GCP Storage Manager initialized")
    
    def _get_or_create_bucket(self, bucket_name: str) -> Bucket:
        """Get existing bucket or create if it doesn't exist"""
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.reload()  # Check if bucket exists
            return bucket
        except exceptions.NotFound:
            logger.info(f"Creating bucket: {bucket_name}")
            bucket = self.client.create_bucket(
                bucket_name,
                location=self.settings.region
            )
            
            # Set lifecycle policy for cost optimization
            self._set_bucket_lifecycle_policy(bucket)
            return bucket
    
    def _set_bucket_lifecycle_policy(self, bucket: Bucket):
        """Set lifecycle policy for automatic storage class transitions"""
        lifecycle_rules = [
            {
                "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                "condition": {"age": 30}  # Move to nearline after 30 days
            },
            {
                "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                "condition": {"age": 90}  # Move to coldline after 90 days
            },
            {
                "action": {"type": "Delete"},
                "condition": {"age": 2555}  # Delete after 7 years
            }
        ]
        
        bucket.lifecycle_rules = lifecycle_rules
        bucket.patch()
        logger.info(f"Set lifecycle policy for bucket: {bucket.name}")
    
    async def store_scraped_content(self, session_id: str, url: str, 
                                  content: str, metadata: Optional[Dict] = None) -> str:
        """Store scraped HTML content and return GCS path"""
        try:
            # Generate structured path
            domain = urlparse(url).netloc.replace('www.', '')
            content_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            timestamp = datetime.utcnow().strftime("%Y%m%d")
            
            blob_path = f"scraped/{session_id}/{timestamp}/{domain}/{content_hash}.html"
            
            # Prepare metadata
            blob_metadata = {
                'session_id': session_id,
                'source_url': url,
                'content_type': 'text/html',
                'scraped_at': datetime.utcnow().isoformat(),
                'content_hash': content_hash,
                'content_length': str(len(content))
            }
            
            if metadata:
                blob_metadata.update(metadata)
            
            # Upload to GCS
            blob = self.content_bucket.blob(blob_path)
            blob.metadata = blob_metadata
            
            # Use async upload for better performance
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: blob.upload_from_string(content, content_type='text/html')
            )
            
            gcs_path = f"gs://{self.content_bucket.name}/{blob_path}"
            logger.info(f"Stored scraped content: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to store scraped content for {url}: {e}")
            raise
    
    async def get_scraped_content(self, gcs_path: str) -> Optional[str]:
        """Retrieve scraped content from GCS"""
        try:
            # Parse GCS path
            if not gcs_path.startswith('gs://'):
                raise ValueError(f"Invalid GCS path format: {gcs_path}")
            
            parts = gcs_path.replace('gs://', '').split('/', 1)
            bucket_name, blob_path = parts[0], parts[1]
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            # Download content asynchronously
            content = await asyncio.get_event_loop().run_in_executor(
                None, 
                blob.download_as_text
            )
            
            return content
            
        except exceptions.NotFound:
            logger.warning(f"Content not found at {gcs_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve content from {gcs_path}: {e}")
            return None
    
    async def store_embeddings_data(self, session_id: str, 
                                  embeddings_data: Dict[str, Any]) -> str:
        """Store vector embeddings data in JSONL format"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_path = f"embeddings/{session_id}/embeddings_{timestamp}.jsonl"
            
            # Convert embeddings to JSONL format
            jsonl_content = ""
            for chunk_id, data in embeddings_data.items():
                jsonl_content += json.dumps({
                    'id': chunk_id,
                    'embedding': data['embedding'],
                    'metadata': data['metadata']
                }) + "\n"
            
            # Upload to embeddings bucket
            blob = self.embeddings_bucket.blob(blob_path)
            blob.metadata = {
                'session_id': session_id,
                'embedding_count': str(len(embeddings_data)),
                'created_at': datetime.utcnow().isoformat()
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob.upload_from_string(jsonl_content, content_type='application/x-jsonlines')
            )
            
            gcs_path = f"gs://{self.embeddings_bucket.name}/{blob_path}"
            logger.info(f"Stored embeddings data: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to store embeddings for {session_id}: {e}")
            raise
    
    async def store_analysis_report(self, session_id: str, analysis_id: str,
                                  report_content: str, format_type: str = 'html') -> str:
        """Store analysis report (HTML, PDF, etc.)"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_extension = format_type.lower()
            blob_path = f"reports/{session_id}/{analysis_id}_{timestamp}.{file_extension}"
            
            # Determine content type
            content_type_map = {
                'html': 'text/html',
                'pdf': 'application/pdf',
                'json': 'application/json',
                'csv': 'text/csv'
            }
            content_type = content_type_map.get(file_extension, 'text/plain')
            
            # Upload to reports bucket
            blob = self.reports_bucket.blob(blob_path)
            blob.metadata = {
                'session_id': session_id,
                'analysis_id': analysis_id,
                'report_type': format_type,
                'created_at': datetime.utcnow().isoformat()
            }
            
            if isinstance(report_content, str):
                upload_func = lambda: blob.upload_from_string(report_content, content_type=content_type)
            else:
                upload_func = lambda: blob.upload_from_string(report_content)
            
            await asyncio.get_event_loop().run_in_executor(None, upload_func)
            
            gcs_path = f"gs://{self.reports_bucket.name}/{blob_path}"
            logger.info(f"Stored analysis report: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to store report for {session_id}/{analysis_id}: {e}")
            raise
    
    async def batch_delete_content(self, session_id: str) -> int:
        """Delete all content for a session (cleanup)"""
        try:
            deleted_count = 0
            
            # Delete from all buckets
            for bucket in [self.content_bucket, self.embeddings_bucket, self.reports_bucket]:
                blobs = bucket.list_blobs(prefix=f"scraped/{session_id}/")
                blob_names = [blob.name for blob in blobs]
                
                if blob_names:
                    # Batch delete for efficiency
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: bucket.delete_blobs(blob_names)
                    )
                    deleted_count += len(blob_names)
            
            logger.info(f"Deleted {deleted_count} objects for session {session_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete content for session {session_id}: {e}")
            return 0
    
    def generate_signed_url(self, gcs_path: str, expiration_hours: int = 1) -> str:
        """Generate signed URL for temporary access to private content"""
        try:
            parts = gcs_path.replace('gs://', '').split('/', 1)
            bucket_name, blob_path = parts[0], parts[1]
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            from datetime import timedelta
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            
            return signed_url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {gcs_path}: {e}")
            return ""

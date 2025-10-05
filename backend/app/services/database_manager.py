"""
Database Manager for Validatus Platform
Handles persistent storage for topics, URLs, scraped content, and analysis scores
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages persistent storage using SQLite database"""
    
    def __init__(self, db_path: str = "validatus_data.db"):
        """Initialize database manager with SQLite backend"""
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
        logger.info(f"DatabaseManager initialized with SQLite database: {self.db_path}")
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Topics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    description TEXT,
                    search_queries TEXT,  -- JSON array
                    initial_urls TEXT,    -- JSON array
                    analysis_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT         -- JSON object
                )
            ''')
            
            # URLs table (for collected URLs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    source TEXT,          -- 'search', 'manual', 'scraped'
                    status TEXT,          -- 'pending', 'scraped', 'failed'
                    metadata TEXT,        -- JSON object
                    FOREIGN KEY (session_id) REFERENCES topics (session_id)
                )
            ''')
            
            # Scraped content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    scraped_at TEXT NOT NULL,
                    processing_status TEXT, -- 'pending', 'processed', 'failed'
                    metadata TEXT,          -- JSON object
                    FOREIGN KEY (session_id) REFERENCES topics (session_id)
                )
            ''')
            
            # Analysis scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,  -- 'market_analysis', 'competitive_analysis', etc.
                    score REAL,
                    confidence REAL,
                    analysis_data TEXT,           -- JSON object with detailed analysis
                    created_at TEXT NOT NULL,
                    metadata TEXT,                -- JSON object
                    FOREIGN KEY (session_id) REFERENCES topics (session_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_topics_status ON topics (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_urls_session_id ON topic_urls (session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_session_id ON scraped_content (session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_session_id ON analysis_scores (session_id)')
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    
    def create_topic(self, topic_data: Dict[str, Any]) -> bool:
        """Create a new topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO topics (
                        session_id, topic, description, search_queries, initial_urls,
                        analysis_type, user_id, status, created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    topic_data['session_id'],
                    topic_data['topic'],
                    topic_data['description'],
                    json.dumps(topic_data.get('search_queries', [])),
                    json.dumps(topic_data.get('initial_urls', [])),
                    topic_data['analysis_type'],
                    topic_data['user_id'],
                    topic_data['status'],
                    topic_data['created_at'],
                    topic_data['updated_at'],
                    json.dumps(topic_data.get('metadata', {}))
                ))
                
                conn.commit()
                logger.info(f"Topic created in database: {topic_data['session_id']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create topic: {e}")
            return False
    
    def get_topic(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a topic by session ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM topics WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    topic_data = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    topic_data['search_queries'] = json.loads(topic_data['search_queries'] or '[]')
                    topic_data['initial_urls'] = json.loads(topic_data['initial_urls'] or '[]')
                    topic_data['metadata'] = json.loads(topic_data['metadata'] or '{}')
                    
                    return topic_data
                    
                return None
                
        except Exception as e:
            logger.error(f"Failed to get topic {session_id}: {e}")
            return None
    
    def update_topic(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                set_clauses = []
                values = []
                
                for key, value in update_data.items():
                    if key == 'search_queries' or key == 'initial_urls':
                        value = json.dumps(value)
                    elif key == 'metadata':
                        value = json.dumps(value)
                    
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                # Always update the updated_at timestamp
                set_clauses.append("updated_at = ?")
                values.append(datetime.utcnow().isoformat())
                values.append(session_id)
                
                query = f"UPDATE topics SET {', '.join(set_clauses)} WHERE session_id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                logger.info(f"Topic updated in database: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update topic {session_id}: {e}")
            return False
    
    def delete_topic(self, session_id: str) -> bool:
        """Delete a topic and all related data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete related data first (due to foreign key constraints)
                cursor.execute('DELETE FROM analysis_scores WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM scraped_content WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM topic_urls WHERE session_id = ?', (session_id,))
                cursor.execute('DELETE FROM topics WHERE session_id = ?', (session_id,))
                
                conn.commit()
                logger.info(f"Topic and related data deleted: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete topic {session_id}: {e}")
            return False
    
    def list_topics(self, user_id: str = None, limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """List topics with optional filtering and return total count"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build base query for counting
                count_query = "SELECT COUNT(*) FROM topics"
                count_params = []
                
                if user_id:
                    count_query += " WHERE user_id = ?"
                    count_params.append(user_id)
                
                # Get total count
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]
                
                # Build query for fetching topics
                query = "SELECT * FROM topics"
                params = []
                
                if user_id:
                    query += " WHERE user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                topics = []
                
                for row in rows:
                    topic_data = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    topic_data['search_queries'] = json.loads(topic_data['search_queries'] or '[]')
                    topic_data['initial_urls'] = json.loads(topic_data['initial_urls'] or '[]')
                    topic_data['metadata'] = json.loads(topic_data['metadata'] or '{}')
                    
                    topics.append(topic_data)
                
                return topics, total_count
                
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            return [], 0
    
    def add_urls(self, session_id: str, urls: List[str], source: str = 'search') -> bool:
        """Add URLs to a topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                current_time = datetime.utcnow().isoformat()
                
                for url in urls:
                    cursor.execute('''
                        INSERT OR IGNORE INTO topic_urls (
                            session_id, url, collected_at, source, status
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, url, current_time, source, 'pending'))
                
                conn.commit()
                logger.info(f"Added {len(urls)} URLs to topic {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add URLs to topic {session_id}: {e}")
            return False
    
    def get_urls(self, session_id: str) -> List[Dict[str, Any]]:
        """Get URLs for a topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT url, collected_at, source, status, metadata 
                    FROM topic_urls 
                    WHERE session_id = ? 
                    ORDER BY collected_at DESC
                ''', (session_id,))
                
                rows = cursor.fetchall()
                urls = []
                
                for row in rows:
                    urls.append({
                        'url': row[0],
                        'collected_at': row[1],
                        'source': row[2],
                        'status': row[3],
                        'metadata': json.loads(row[4] or '{}')
                    })
                
                return urls
                
        except Exception as e:
            logger.error(f"Failed to get URLs for topic {session_id}: {e}")
            return []
    
    def save_scraped_content(self, session_id: str, url: str, title: str, content: str, metadata: Dict = None) -> bool:
        """Save scraped content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO scraped_content (
                        session_id, url, title, content, scraped_at, 
                        processing_status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, url, title, content, 
                    datetime.utcnow().isoformat(), 'processed',
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                logger.info(f"Scraped content saved for {url}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save scraped content for {url}: {e}")
            return False
    
    def save_analysis_score(self, session_id: str, analysis_type: str, score: float, 
                           confidence: float, analysis_data: Dict, metadata: Dict = None) -> bool:
        """Save analysis scores"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO analysis_scores (
                        session_id, analysis_type, score, confidence,
                        analysis_data, created_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, analysis_type, score, confidence,
                    json.dumps(analysis_data), datetime.utcnow().isoformat(),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                logger.info(f"Analysis score saved for topic {session_id}: {analysis_type}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save analysis score for topic {session_id}: {e}")
            return False
    
    def get_analysis_scores(self, session_id: str) -> List[Dict[str, Any]]:
        """Get analysis scores for a topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT analysis_type, score, confidence, analysis_data, 
                           created_at, metadata 
                    FROM analysis_scores 
                    WHERE session_id = ? 
                    ORDER BY created_at DESC
                ''', (session_id,))
                
                rows = cursor.fetchall()
                scores = []
                
                for row in rows:
                    scores.append({
                        'analysis_type': row[0],
                        'score': row[1],
                        'confidence': row[2],
                        'analysis_data': json.loads(row[3] or '{}'),
                        'created_at': row[4],
                        'metadata': json.loads(row[5] or '{}')
                    })
                
                return scores
                
        except Exception as e:
            logger.error(f"Failed to get analysis scores for topic {session_id}: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count topics
                cursor.execute('SELECT COUNT(*) FROM topics')
                stats['total_topics'] = cursor.fetchone()[0]
                
                # Count URLs
                cursor.execute('SELECT COUNT(*) FROM topic_urls')
                stats['total_urls'] = cursor.fetchone()[0]
                
                # Count scraped content
                cursor.execute('SELECT COUNT(*) FROM scraped_content')
                stats['total_scraped_content'] = cursor.fetchone()[0]
                
                # Count analysis scores
                cursor.execute('SELECT COUNT(*) FROM analysis_scores')
                stats['total_analysis_scores'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()

"""Google Custom Search Integration Schema

Revision ID: 003
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Google Custom Search specific columns to url_collection_campaigns
    op.add_column('url_collection_campaigns', sa.Column('search_api_used', sa.VARCHAR(50), nullable=True, server_default='google_custom_search'))
    op.add_column('url_collection_campaigns', sa.Column('api_quota_used', sa.INTEGER(), nullable=True, server_default='0'))
    op.add_column('url_collection_campaigns', sa.Column('search_language', sa.VARCHAR(10), nullable=True, server_default='en'))
    op.add_column('url_collection_campaigns', sa.Column('safe_search_level', sa.VARCHAR(20), nullable=True, server_default='medium'))
    
    # Create search_queries table
    op.create_table('search_queries',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.VARCHAR(50), nullable=False),
        sa.Column('campaign_id', sa.INTEGER(), nullable=True),
        sa.Column('query_text', sa.TEXT(), nullable=False),
        sa.Column('total_results_found', sa.BIGINT(), nullable=True, server_default=sa.text('0')),
        sa.Column('results_retrieved', sa.INTEGER(), nullable=True, server_default=sa.text('0')),
        sa.Column('search_time_ms', sa.INTEGER(), nullable=True, server_default=sa.text('0')),
        sa.Column('api_quota_cost', sa.INTEGER(), nullable=True, server_default=sa.text('1')),
        sa.Column('executed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['session_id'], ['topics.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['url_collection_campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add Google Custom Search specific metadata to topic_urls
    op.add_column('topic_urls', sa.Column('search_rank', sa.INTEGER(), nullable=True))
    op.add_column('topic_urls', sa.Column('search_query', sa.TEXT(), nullable=True))
    op.add_column('topic_urls', sa.Column('snippet', sa.TEXT(), nullable=True))
    op.add_column('topic_urls', sa.Column('formatted_url', sa.TEXT(), nullable=True))
    
    # Create indexes for better performance
    op.create_index('idx_search_queries_session_id', 'search_queries', ['session_id'])
    op.create_index('idx_search_queries_campaign_id', 'search_queries', ['campaign_id'])
    op.create_index('idx_topic_urls_search_query', 'topic_urls', ['search_query'])
    op.create_index('idx_topic_urls_search_rank', 'topic_urls', ['search_rank'])
    
    # Create view for URL collection summary
    op.execute("""
        CREATE OR REPLACE VIEW url_collection_summary AS
        SELECT 
            t.session_id,
            t.topic,
            t.user_id,
            t.status as topic_status,
            c.campaign_name,
            c.collection_strategy,
            c.status as campaign_status,
            c.urls_discovered,
            c.urls_processed,
            c.created_at as campaign_created,
            c.completed_at as campaign_completed,
            COUNT(u.id) as urls_in_database,
            COUNT(CASE WHEN u.status = 'pending' THEN 1 END) as urls_pending,
            COUNT(CASE WHEN u.status = 'processing' THEN 1 END) as urls_processing,
            COUNT(CASE WHEN u.status = 'scraped' THEN 1 END) as urls_scraped,
            COUNT(CASE WHEN u.status = 'failed' THEN 1 END) as urls_failed
        FROM topics t
        LEFT JOIN url_collection_campaigns c ON t.session_id = c.session_id
        LEFT JOIN topic_urls u ON t.session_id = u.session_id
        GROUP BY t.session_id, t.topic, t.user_id, t.status, 
                 c.campaign_name, c.collection_strategy, c.status,
                 c.urls_discovered, c.urls_processed, c.created_at, c.completed_at;
    """)
    
    # Grant permissions
    op.execute("GRANT SELECT ON url_collection_summary TO validatus_app;")
    op.execute("GRANT ALL PRIVILEGES ON search_queries TO validatus_app;")
    op.execute("GRANT ALL PRIVILEGES ON SEQUENCE search_queries_id_seq TO validatus_app;")


def downgrade() -> None:
    # Drop view
    op.execute("DROP VIEW IF EXISTS url_collection_summary;")
    
    # Drop indexes
    op.drop_index('idx_topic_urls_search_rank', table_name='topic_urls')
    op.drop_index('idx_topic_urls_search_query', table_name='topic_urls')
    op.drop_index('idx_search_queries_campaign_id', table_name='search_queries')
    op.drop_index('idx_search_queries_session_id', table_name='search_queries')
    
    # Drop columns from topic_urls
    op.drop_column('topic_urls', 'formatted_url')
    op.drop_column('topic_urls', 'snippet')
    op.drop_column('topic_urls', 'search_query')
    op.drop_column('topic_urls', 'search_rank')
    
    # Drop search_queries table
    op.drop_table('search_queries')
    
    # Drop columns from url_collection_campaigns
    op.drop_column('url_collection_campaigns', 'safe_search_level')
    op.drop_column('url_collection_campaigns', 'search_language')
    op.drop_column('url_collection_campaigns', 'api_quota_used')
    op.drop_column('url_collection_campaigns', 'search_api_used')

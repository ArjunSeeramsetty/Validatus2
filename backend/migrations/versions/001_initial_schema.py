"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create topics table
    op.create_table('topics',
        sa.Column('session_id', sa.VARCHAR(50), nullable=False),
        sa.Column('topic', sa.VARCHAR(255), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('user_id', sa.VARCHAR(100), nullable=False),
        sa.Column('status', sa.VARCHAR(50), nullable=False, server_default='CREATED'),
        sa.Column('analysis_type', sa.VARCHAR(50), nullable=False, server_default='COMPREHENSIVE'),
        sa.Column('search_queries', postgresql.ARRAY(sa.TEXT()), nullable=True, server_default='{}'),
        sa.Column('initial_urls', postgresql.ARRAY(sa.TEXT()), nullable=True, server_default='{}'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('session_id'),
        sa.CheckConstraint("status IN ('CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED')", name='chk_status'),
        sa.CheckConstraint("analysis_type IN ('STANDARD', 'COMPREHENSIVE')", name='chk_analysis_type')
    )
    
    # Create workflow_status table
    op.create_table('workflow_status',
        sa.Column('session_id', sa.VARCHAR(50), nullable=False),
        sa.Column('current_stage', sa.VARCHAR(50), nullable=False),
        sa.Column('stages_completed', postgresql.ARRAY(sa.TEXT()), nullable=True, server_default='{}'),
        sa.Column('stage_progress', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('error_message', sa.TEXT(), nullable=True),
        sa.Column('retry_count', sa.INTEGER(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['session_id'], ['topics.session_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id'),
        sa.CheckConstraint("current_stage IN ('CREATED', 'URL_COLLECTION', 'URL_SCRAPING', 'CONTENT_PROCESSING', 'VECTOR_CREATION', 'ANALYSIS', 'COMPLETED', 'FAILED')", name='chk_current_stage')
    )
    
    # Create indexes
    op.create_index('idx_topics_user_id', 'topics', ['user_id'])
    op.create_index('idx_topics_created_at', 'topics', ['created_at'], unique=False, postgresql_using='btree')
    op.create_index('idx_topics_status', 'topics', ['status'])
    op.create_index('idx_workflow_status_stage', 'workflow_status', ['current_stage'])
    op.create_index('idx_workflow_status_updated', 'workflow_status', ['updated_at'], unique=False, postgresql_using='btree')
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create triggers
    op.execute("""
        CREATE TRIGGER update_topics_updated_at 
        BEFORE UPDATE ON topics
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_workflow_status_updated_at 
        BEFORE UPDATE ON workflow_status
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_workflow_status_updated_at ON workflow_status;")
    op.execute("DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Drop indexes
    op.drop_index('idx_workflow_status_updated', table_name='workflow_status')
    op.drop_index('idx_workflow_status_stage', table_name='workflow_status')
    op.drop_index('idx_topics_status', table_name='topics')
    op.drop_index('idx_topics_created_at', table_name='topics')
    op.drop_index('idx_topics_user_id', table_name='topics')
    
    # Drop tables
    op.drop_table('workflow_status')
    op.drop_table('topics')

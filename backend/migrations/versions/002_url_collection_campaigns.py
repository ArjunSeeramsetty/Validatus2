"""Create URL Collection Campaigns Table

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create url_collection_campaigns table
    op.create_table('url_collection_campaigns',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('session_id', sa.VARCHAR(50), nullable=False),
        sa.Column('campaign_name', sa.VARCHAR(200), nullable=True),
        sa.Column('status', sa.VARCHAR(50), nullable=False, server_default='pending'),
        sa.Column('total_urls_collected', sa.INTEGER(), nullable=False, server_default='0'),
        sa.Column('total_queries_processed', sa.INTEGER(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('error_message', sa.TEXT(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['topics.session_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for performance
    op.create_index('idx_url_collection_campaigns_session_id', 'url_collection_campaigns', ['session_id'])
    op.create_index('idx_url_collection_campaigns_status', 'url_collection_campaigns', ['status'])


def downgrade() -> None:
    op.drop_index('idx_url_collection_campaigns_status', table_name='url_collection_campaigns')
    op.drop_index('idx_url_collection_campaigns_session_id', table_name='url_collection_campaigns')
    op.drop_table('url_collection_campaigns')

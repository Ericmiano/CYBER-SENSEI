"""
Alembic migration to add database constraints and indexes.

Adds:
- Foreign key relationships with cascade rules
- Unique constraints on key fields
- Check constraints for enums
- Indexes for performance
- Created/updated timestamps
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Apply constraints and indexes."""
    
    # ==================== MODULES TABLE ====================
    # Add unique constraint on name
    op.create_unique_constraint('uq_module_name', 'module', ['name'])
    
    # Add indexes for common queries
    op.create_index('idx_module_created_by', 'module', ['created_by'])
    op.create_index('idx_module_created_at', 'module', ['created_at'])
    
    # ==================== TOPICS TABLE ====================
    # Add unique constraint on name per module
    op.create_unique_constraint('uq_topic_name_per_module', 'topic', ['name', 'module_id'])
    
    # Add check constraint for difficulty
    op.create_check_constraint(
        'ck_topic_difficulty',
        'topic',
        "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')"
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_topic_module_id',
        'topic', 'module',
        ['module_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add indexes
    op.create_index('idx_topic_module_id', 'topic', ['module_id'])
    op.create_index('idx_topic_created_by', 'topic', ['created_by'])
    op.create_index('idx_topic_order', 'topic', ['module_id', 'order'])
    
    # ==================== RESOURCES TABLE ====================
    # Add check constraint for resource_type
    op.create_check_constraint(
        'ck_resource_type',
        'resource',
        "resource_type IN ('video', 'article', 'pdf', 'interactive', 'code_snippet', 'challenge')"
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_resource_topic_id',
        'resource', 'topic',
        ['topic_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add indexes
    op.create_index('idx_resource_topic_id', 'resource', ['topic_id'])
    op.create_index('idx_resource_uploaded_by', 'resource', ['uploaded_by'])
    op.create_index('idx_resource_type', 'resource', ['resource_type'])
    op.create_index('idx_resource_uploaded_at', 'resource', ['uploaded_at'])
    
    # ==================== QUIZ_QUESTION TABLE ====================
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_quiz_question_topic_id',
        'quiz_question', 'topic',
        ['topic_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add indexes
    op.create_index('idx_quiz_question_topic_id', 'quiz_question', ['topic_id'])
    op.create_index('idx_quiz_question_created_by', 'quiz_question', ['created_by'])
    
    # ==================== USER_PROGRESS TABLE ====================
    # Add unique constraint on user_topic combination
    op.create_unique_constraint(
        'uq_user_progress_user_topic',
        'user_progress',
        ['user_id', 'topic_id']
    )
    
    # Add check constraint for percentage
    op.create_check_constraint(
        'ck_user_progress_percentage',
        'user_progress',
        'completion_percentage >= 0 AND completion_percentage <= 100'
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_user_progress_topic_id',
        'user_progress', 'topic',
        ['topic_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add indexes
    op.create_index('idx_user_progress_user_id', 'user_progress', ['user_id'])
    op.create_index('idx_user_progress_topic_id', 'user_progress', ['topic_id'])
    op.create_index('idx_user_progress_last_accessed', 'user_progress', ['last_accessed'])
    
    # ==================== PROJECT TABLE ====================
    # Add check constraint for status
    op.create_check_constraint(
        'ck_project_status',
        'project',
        "status IN ('planning', 'in_progress', 'completed', 'on_hold')"
    )
    
    # Add indexes
    op.create_index('idx_project_owner', 'project', ['owner'])
    op.create_index('idx_project_status', 'project', ['status'])
    op.create_index('idx_project_created_at', 'project', ['created_at'])


def downgrade():
    """Remove constraints and indexes."""
    
    # Drop indexes (in reverse order)
    op.drop_index('idx_project_created_at', 'project')
    op.drop_index('idx_project_status', 'project')
    op.drop_index('idx_project_owner', 'project')
    
    # Drop constraints
    op.drop_constraint('ck_project_status', 'project', type_='check')
    
    op.drop_index('idx_user_progress_last_accessed', 'user_progress')
    op.drop_index('idx_user_progress_topic_id', 'user_progress')
    op.drop_index('idx_user_progress_user_id', 'user_progress')
    
    op.drop_constraint('fk_user_progress_topic_id', 'user_progress', type_='foreignkey')
    op.drop_constraint('ck_user_progress_percentage', 'user_progress', type_='check')
    op.drop_constraint('uq_user_progress_user_topic', 'user_progress', type_='unique')
    
    op.drop_index('idx_quiz_question_created_by', 'quiz_question')
    op.drop_index('idx_quiz_question_topic_id', 'quiz_question')
    op.drop_constraint('fk_quiz_question_topic_id', 'quiz_question', type_='foreignkey')
    
    op.drop_index('idx_resource_uploaded_at', 'resource')
    op.drop_index('idx_resource_type', 'resource')
    op.drop_index('idx_resource_uploaded_by', 'resource')
    op.drop_index('idx_resource_topic_id', 'resource')
    op.drop_constraint('fk_resource_topic_id', 'resource', type_='foreignkey')
    op.drop_constraint('ck_resource_type', 'resource', type_='check')
    
    op.drop_index('idx_topic_order', 'topic')
    op.drop_index('idx_topic_created_by', 'topic')
    op.drop_index('idx_topic_module_id', 'topic')
    op.drop_constraint('fk_topic_module_id', 'topic', type_='foreignkey')
    op.drop_constraint('ck_topic_difficulty', 'topic', type_='check')
    op.drop_constraint('uq_topic_name_per_module', 'topic', type_='unique')
    
    op.drop_index('idx_module_created_at', 'module')
    op.drop_index('idx_module_created_by', 'module')
    op.drop_constraint('uq_module_name', 'module', type_='unique')

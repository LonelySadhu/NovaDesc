"""initial

Revision ID: 237a29b4e103
Revises: 
Create Date: 2026-03-30 18:19:45.770422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '237a29b4e103'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # pgvector extension — required for document_chunks.embedding column
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # departments создаём без head_id FK (циклическая зависимость с users)
    # FK добавляется отдельно после создания users
    op.create_table('departments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('head_id', sa.UUID(), nullable=True),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=32), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('department_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # Теперь добавляем FK departments.head_id → users (после создания users)
    op.create_foreign_key(
        'fk_departments_head_id_users', 'departments', 'users',
        ['head_id'], ['id'], ondelete='SET NULL'
    )
    op.create_table('equipment_systems',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('system_type', sa.String(length=64), nullable=True),
    sa.Column('department_id', sa.UUID(), nullable=False),
    sa.Column('stakeholder_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['stakeholder_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipment',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('serial_number', sa.String(length=128), nullable=False),
    sa.Column('manufacturer', sa.String(length=255), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('system_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('maintenance_interval_value', sa.Integer(), nullable=True),
    sa.Column('maintenance_interval_unit', sa.String(length=16), nullable=True),
    sa.Column('installed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['system_id'], ['equipment_systems.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_serial_number'), 'equipment', ['serial_number'], unique=True)
    op.create_index(op.f('ix_equipment_status'), 'equipment', ['status'], unique=False)
    op.create_table('knowledge_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('doc_type', sa.String(length=16), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('equipment_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('chunk_count', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=512), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_documents_equipment_id'), 'knowledge_documents', ['equipment_id'], unique=False)
    op.create_table('maintenance_schedules',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('equipment_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('interval_value', sa.Integer(), nullable=False),
    sa.Column('interval_unit', sa.String(length=16), nullable=False),
    sa.Column('last_performed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_schedules_equipment_id'), 'maintenance_schedules', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_maintenance_schedules_next_due_at'), 'maintenance_schedules', ['next_due_at'], unique=False)
    op.create_table('spare_parts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('equipment_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('part_number', sa.String(length=128), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('min_stock_level', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=False),
    sa.Column('stock_location', sa.String(length=255), nullable=True),
    sa.Column('unit_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spare_parts_equipment_id'), 'spare_parts', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_spare_parts_part_number'), 'spare_parts', ['part_number'], unique=False)
    op.create_table('work_orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('equipment_id', sa.UUID(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('order_type', sa.String(length=32), nullable=False),
    sa.Column('priority', sa.String(length=16), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('assigned_to', sa.UUID(), nullable=True),
    sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('on_hold_reason', sa.Text(), nullable=True),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_orders_equipment_id'), 'work_orders', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_work_orders_status'), 'work_orders', ['status'], unique=False)
    op.create_table('ai_queries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=True),
    sa.Column('context_equipment_id', sa.UUID(), nullable=True),
    sa.Column('context_work_order_id', sa.UUID(), nullable=True),
    sa.Column('model_used', sa.String(length=64), nullable=False),
    sa.Column('tokens_used', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['context_equipment_id'], ['equipment.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['context_work_order_id'], ['work_orders.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_queries_user_id'), 'ai_queries', ['user_id'], unique=False)
    op.create_table('document_chunks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('chunk_index', sa.Integer(), nullable=False),
    sa.Column('embedding', Vector(768), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_table('purchase_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('spare_part_id', sa.UUID(), nullable=False),
    sa.Column('requested_by', sa.UUID(), nullable=False),
    sa.Column('quantity_needed', sa.Integer(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('approved_by', sa.UUID(), nullable=True),
    sa.Column('rejected_reason', sa.Text(), nullable=True),
    sa.Column('supplier', sa.String(length=255), nullable=True),
    sa.Column('estimated_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('external_reference', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['spare_part_id'], ['spare_parts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_requests_spare_part_id'), 'purchase_requests', ['spare_part_id'], unique=False)
    op.create_index(op.f('ix_purchase_requests_status'), 'purchase_requests', ['status'], unique=False)
    op.create_table('spare_part_movements',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('spare_part_id', sa.UUID(), nullable=False),
    sa.Column('quantity_delta', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=512), nullable=False),
    sa.Column('work_order_id', sa.UUID(), nullable=True),
    sa.Column('write_off_reason', sa.String(length=64), nullable=True),
    sa.Column('performed_by', sa.UUID(), nullable=True),
    sa.Column('unit_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['spare_part_id'], ['spare_parts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spare_part_movements_spare_part_id'), 'spare_part_movements', ['spare_part_id'], unique=False)
    op.create_table('work_order_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('work_order_id', sa.UUID(), nullable=False),
    sa.Column('author_id', sa.UUID(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('hours_spent', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_order_logs_work_order_id'), 'work_order_logs', ['work_order_id'], unique=False)
    op.create_table('work_order_photos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('work_order_id', sa.UUID(), nullable=False),
    sa.Column('uploaded_by', sa.UUID(), nullable=False),
    sa.Column('file_path', sa.String(length=512), nullable=False),
    sa.Column('original_filename', sa.String(length=255), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('caption', sa.String(length=512), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_order_photos_work_order_id'), 'work_order_photos', ['work_order_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_work_order_photos_work_order_id'), table_name='work_order_photos')
    op.drop_table('work_order_photos')
    op.drop_index(op.f('ix_work_order_logs_work_order_id'), table_name='work_order_logs')
    op.drop_table('work_order_logs')
    op.drop_index(op.f('ix_spare_part_movements_spare_part_id'), table_name='spare_part_movements')
    op.drop_table('spare_part_movements')
    op.drop_index(op.f('ix_purchase_requests_status'), table_name='purchase_requests')
    op.drop_index(op.f('ix_purchase_requests_spare_part_id'), table_name='purchase_requests')
    op.drop_table('purchase_requests')
    op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_index(op.f('ix_ai_queries_user_id'), table_name='ai_queries')
    op.drop_table('ai_queries')
    op.drop_index(op.f('ix_work_orders_status'), table_name='work_orders')
    op.drop_index(op.f('ix_work_orders_equipment_id'), table_name='work_orders')
    op.drop_table('work_orders')
    op.drop_index(op.f('ix_spare_parts_part_number'), table_name='spare_parts')
    op.drop_index(op.f('ix_spare_parts_equipment_id'), table_name='spare_parts')
    op.drop_table('spare_parts')
    op.drop_index(op.f('ix_maintenance_schedules_next_due_at'), table_name='maintenance_schedules')
    op.drop_index(op.f('ix_maintenance_schedules_equipment_id'), table_name='maintenance_schedules')
    op.drop_table('maintenance_schedules')
    op.drop_index(op.f('ix_knowledge_documents_equipment_id'), table_name='knowledge_documents')
    op.drop_table('knowledge_documents')
    op.drop_index(op.f('ix_equipment_status'), table_name='equipment')
    op.drop_index(op.f('ix_equipment_serial_number'), table_name='equipment')
    op.drop_table('equipment')
    op.drop_table('equipment_systems')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_constraint('fk_departments_head_id_users', 'departments', type_='foreignkey')
    op.drop_table('departments')
    op.execute("DROP EXTENSION IF EXISTS vector")
    # ### end Alembic commands ###

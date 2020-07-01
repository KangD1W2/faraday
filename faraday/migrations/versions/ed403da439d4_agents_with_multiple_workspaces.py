"""Agents with multiple workspaces

Revision ID: ed403da439d4
Revises: 9c678c44aa61
Create Date: 2020-07-01 22:12:46.001776+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed403da439d4'
down_revision = '9c678c44aa61'
branch_labels = None
depends_on = None


def upgrade():

    # CREATE NEW TABLE (M2M relationship)
    op.create_table(
        'association_workspace_and_agents_table',
        sa.Column('workspace_id', sa.Integer, sa.ForeignKey('workspace.id')),
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agent.id'))
    )
    # MIGRATE DATA -> TAKE THE ONLY WORKSPACE AND LINK IN THE NEW TABLE

    conn = op.get_bind()
    conn.execute("""
    INSERT INTO association_workspace_and_agents_table (workspace_id, agent_id)
    SELECT workspace_id, id FROM agent
    """)

    # DROP OLD COLUMN AND FK
    op.drop_constraint('agent_workspace_id_fkey', 'agent')
    op.drop_column('agent', 'workspace_id')


def downgrade():
    # ADD OLD COLUMN AND FK
    op.add_column(
        'agent',
        sa.Column('workspace_id', sa.Integer),
    )
    op.create_foreign_key(
        'agent_workspace_id_fkey',
        'agent',
        'workspace', ['workspace_id'], ['id']
    )

    # MIGRATE DATA

    conn = op.get_bind()
    conn.execute("""
    UPDATE agent
    SET workspace_id=wa.workspace_id
    FROM agent as a
         INNER JOIN association_workspace_and_agents_table wa 
             ON wa.agent_id = a.id
    WHERE 
      agent.id=a.id;
    """)

    op.alter_column(
        'agent',
        'workspace_id',
        nullable=False
    )

    # DROP NEW TABLE (M2M relationship)
    op.drop_table('association_workspace_and_agents_table')

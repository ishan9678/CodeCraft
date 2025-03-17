"""Initial migration

Revision ID: dd5575873d46
Revises: 
Create Date: 2025-03-18 02:47:38.027221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd5575873d46'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=True),
    sa.Column('question', sa.Text(), nullable=True),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('user_input', sa.String(length=255), nullable=True),
    sa.Column('language', sa.String(length=50), nullable=True),
    sa.Column('max_iterations', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('iterations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('question_id', sa.UUID(), nullable=True),
    sa.Column('iteration_number', sa.Integer(), nullable=True),
    sa.Column('chain_of_thought', sa.Text(), nullable=True),
    sa.Column('generated_code', sa.Text(), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_case_results',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('iteration_id', sa.UUID(), nullable=True),
    sa.Column('input', sa.Text(), nullable=True),
    sa.Column('expected_output', sa.Text(), nullable=True),
    sa.Column('actual_output', sa.Text(), nullable=True),
    sa.Column('execution_time', sa.Float(), nullable=True),
    sa.Column('memory_usage', sa.Integer(), nullable=True),
    sa.Column('stderror', sa.Text(), nullable=True),
    sa.Column('compiler_errors', sa.Text(), nullable=True),
    sa.Column('passed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['iteration_id'], ['iterations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_case_results')
    op.drop_table('iterations')
    op.drop_table('questions')
    # ### end Alembic commands ###

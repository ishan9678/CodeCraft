"""Modify chain_of_thought to list

Revision ID: 200e6381bfde
Revises: dd5575873d46
Create Date: 2025-03-18 23:43:01.907243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY



# revision identifiers, used by Alembic.
revision: str = '200e6381bfde'
down_revision: Union[str, None] = 'dd5575873d46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Convert existing TEXT data to an array format
    op.execute("ALTER TABLE iterations ALTER COLUMN chain_of_thought SET DATA TYPE TEXT[] USING ARRAY[chain_of_thought]")

def downgrade():
    # Convert back to TEXT (taking the first element of the array)
    op.execute("ALTER TABLE iterations ALTER COLUMN chain_of_thought SET DATA TYPE TEXT USING chain_of_thought[1]")

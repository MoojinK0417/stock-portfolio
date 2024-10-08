"""Add total_value column to stocks table

Revision ID: df2862a6b8eb
Revises: 
Create Date: 2024-08-11 01:52:02.785448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df2862a6b8eb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stocks', sa.Column('initial_value', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stocks', 'initial_value')
    # ### end Alembic commands ###

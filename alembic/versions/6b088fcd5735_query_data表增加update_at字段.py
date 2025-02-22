"""query_data表增加update_at字段

Revision ID: 6b088fcd5735
Revises: 85116d4c89d7
Create Date: 2025-02-21 11:23:40.546743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b088fcd5735'
down_revision: Union[str, None] = '85116d4c89d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('query_data', sa.Column('update_at', sa.DateTime(), nullable=False))
    op.create_index(op.f('ix_query_data_update_at'), 'query_data', ['update_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_query_data_update_at'), table_name='query_data')
    op.drop_column('query_data', 'update_at')
    # ### end Alembic commands ###

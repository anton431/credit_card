"""added_table

Revision ID: 246f37f26b29
Revises: 
Create Date: 2023-10-05 10:56:59.921983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '246f37f26b29'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.String(length=20), nullable=True),
    sa.Column('hashed_password', sa.String(length=100), nullable=True),
    sa.Column('limit', sa.DECIMAL(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('_balance', sa.DECIMAL(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('card_number')
    )
    op.create_table('balancelog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.String(length=20), nullable=True),
    sa.Column('before', sa.DECIMAL(), nullable=True),
    sa.Column('after', sa.DECIMAL(), nullable=True),
    sa.Column('changes', sa.DECIMAL(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('_datetime_utc', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('commonlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.String(length=20), nullable=True),
    sa.Column('before', sa.String(length=300), nullable=True),
    sa.Column('after', sa.String(length=300), nullable=True),
    sa.Column('changes', sa.String(length=300), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('_datetime_utc', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('commonlog')
    op.drop_table('balancelog')
    op.drop_table('User')
    # ### end Alembic commands ###

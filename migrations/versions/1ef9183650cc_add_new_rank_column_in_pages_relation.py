"""Add new_rank column in pages relation

Revision ID: 1ef9183650cc
Revises: de85d4fbd2a0
Create Date: 2019-12-17 10:07:11.077608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ef9183650cc'
down_revision = 'de85d4fbd2a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pages', sa.Column('new_rank', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pages', 'new_rank')
    # ### end Alembic commands ###

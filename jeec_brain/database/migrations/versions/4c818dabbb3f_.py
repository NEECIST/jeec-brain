"""empty message

Revision ID: 4c818dabbb3f
Revises: 
Create Date: 2021-11-13 17:49:31.179283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c818dabbb3f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auctions', sa.Column('starting_date', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('auctions', 'starting_date')
    # ### end Alembic commands ###

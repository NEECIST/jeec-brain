"""empty message

Revision ID: 38a73cdef9b5
Revises: 0c3a0aee0167
Create Date: 2022-02-19 19:12:31.680838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38a73cdef9b5'
down_revision = '0c3a0aee0167'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('teams_name_key', 'teams', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('teams_name_key', 'teams', ['name'])
    # ### end Alembic commands ###

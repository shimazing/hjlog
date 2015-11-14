"""empty message

Revision ID: 46ae0d2b68d
Revises: 3c82d9e20c5
Create Date: 2015-11-14 17:21:52.756798

"""

# revision identifiers, used by Alembic.
revision = '46ae0d2b68d'
down_revision = '3c82d9e20c5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo', sa.Column('original_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'photo', 'post', ['original_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'photo', type_='foreignkey')
    op.drop_column('photo', 'original_id')
    ### end Alembic commands ###

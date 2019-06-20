"""about me and last seen fields in user model

Revision ID: 9681be76360a
Revises: 95a8021faf46
Create Date: 2019-05-08 16:02:52.763575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9681be76360a'
down_revision = '95a8021faf46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###
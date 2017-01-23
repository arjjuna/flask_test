"""Added message model

Revision ID: b918c2123775
Revises: e6fbc8aedb05
Create Date: 2017-01-21 18:18:33.078000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b918c2123775'
down_revision = 'e6fbc8aedb05'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=100), nullable=True),
    sa.Column('timestamp', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###

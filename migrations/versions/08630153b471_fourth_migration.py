"""Fourth migration.

Revision ID: 08630153b471
Revises: d3846f3e9213
Create Date: 2020-07-01 00:40:38.785332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08630153b471'
down_revision = 'd3846f3e9213'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("deposit") as batch_op:
        batch_op.add_column(sa.Column('is_successful', sa.Boolean(), nullable=True))
    
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('deposit', 'wallet_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('deposit', 'plan_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('deposit', 'is_successful')
    # ### end Alembic commands ###

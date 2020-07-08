"""sixth migration

Revision ID: bcd4b40d8bff
Revises: c4cc0d359a63
Create Date: 2020-07-02 00:53:01.779086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcd4b40d8bff'
down_revision = 'c4cc0d359a63'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transaction") as batch_op:
        batch_op.alter_column('proof',
                existing_type=sa.BOOLEAN(),
                nullable=True)
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('deposit', 'wallet_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('deposit', 'plan_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('deposit', 'is_successful',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
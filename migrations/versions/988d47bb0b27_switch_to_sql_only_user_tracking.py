"""Switch to SQL-only user tracking

Revision ID: 988d47bb0b27
Revises: 4f111efa00d4
Create Date: 2025-06-12 01:08:40.816617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '988d47bb0b27'
down_revision = '4f111efa00d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.alter_column('question',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=False)
        batch_op.alter_column('explanation',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('has_logged_in_before', sa.Boolean(), nullable=True))
        batch_op.create_unique_constraint(None, ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('has_logged_in_before')
        batch_op.drop_column('email')

    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.alter_column('explanation',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('question',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    # ### end Alembic commands ###

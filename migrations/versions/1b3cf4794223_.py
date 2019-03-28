"""empty message

Revision ID: 1b3cf4794223
Revises: 
Create Date: 2019-03-27 11:53:59.270369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b3cf4794223'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_email'), 'admin', ['email'], unique=True)
    op.create_index(op.f('ix_admin_username'), 'admin', ['username'], unique=True)
    op.create_table('parking_lot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parking_lot_name', sa.String(length=120), nullable=True),
    sa.Column('closed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=False),
    sa.Column('last_name', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.Column('registration_plate', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('admin_parkinglot',
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('parkinglot_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.ForeignKeyConstraint(['parkinglot_id'], ['parking_lot.id'], )
    )
    op.create_table('parking_spot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parking_lot_id', sa.Integer(), nullable=False),
    sa.Column('index_in_parking_lot', sa.String(length=4), nullable=False),
    sa.Column('reserved', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['parking_lot_id'], ['parking_lot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('parking_spot_id', sa.Integer(), nullable=False),
    sa.Column('start_datetime', sa.String(length=120), nullable=False),
    sa.Column('end_datetime', sa.String(length=120), nullable=False),
    sa.ForeignKeyConstraint(['parking_spot_id'], ['parking_spot.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reservation')
    op.drop_table('parking_spot')
    op.drop_table('admin_parkinglot')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('parking_lot')
    op.drop_index(op.f('ix_admin_username'), table_name='admin')
    op.drop_index(op.f('ix_admin_email'), table_name='admin')
    op.drop_table('admin')
    # ### end Alembic commands ###

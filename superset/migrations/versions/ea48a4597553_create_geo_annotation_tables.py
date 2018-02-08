"""create geo annotation tables

Revision ID: ea48a4597553
Revises: 21e88bc06c02
Create Date: 2018-02-08 15:22:37.349138

"""

# revision identifiers, used by Alembic.
revision = 'ea48a4597553'
down_revision = '21e88bc06c02'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'geo_annotation_layer',
        sa.Column('created_on', sa.DateTime(), nullable=True),
        sa.Column('changed_on', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=250), nullable=True),
        sa.Column('descr', sa.Text(), nullable=True),
        sa.Column('changed_by_fk', sa.Integer(), nullable=True),
        sa.Column('created_by_fk', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
        sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'geo_annotation',
        sa.Column('created_on', sa.DateTime(), nullable=True),
        sa.Column('changed_on', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_dttm', sa.DateTime(), nullable=True),
        sa.Column('end_dttm', sa.DateTime(), nullable=True),
        sa.Column('layer_id', sa.Integer(), nullable=True),
        sa.Column('short_descr', sa.String(length=500), nullable=True),
        sa.Column('long_descr', sa.Text(), nullable=True),
        sa.Column('geojson', sa.Text(), nullable=True),
        sa.Column('changed_by_fk', sa.Integer(), nullable=True),
        sa.Column('created_by_fk', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
        sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
        sa.ForeignKeyConstraint(['layer_id'], [u'geo_annotation_layer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ti_geo_annotation',
        'geo_annotation', ['layer_id', 'start_dttm', 'end_dttm'], unique=False)


def downgrade():
    op.drop_index('ti_geo_annotation', table_name='geo_annotation')
    op.drop_table('geo_annotation')
    op.drop_table('geo_annotation_layer')

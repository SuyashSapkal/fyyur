"""empty message

Revision ID: 1ef897a9057d
Revises: f134fef79379
Create Date: 2021-02-01 20:32:30.719452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ef897a9057d'
down_revision = 'f134fef79379'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'venue')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    # ### end Alembic commands ###
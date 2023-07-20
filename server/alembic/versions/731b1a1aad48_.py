"""empty message

Revision ID: 731b1a1aad48
Revises: 
Create Date: 2023-07-13 16:13:30.183686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '731b1a1aad48'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('responsibilities', sa.Text(), nullable=True),
    sa.Column('qualifications', sa.Text(), nullable=True),
    sa.Column('work_mode', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('candidate',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('date_of_birth', sa.String(length=255), nullable=True),
    sa.Column('submited_datetime', sa.DateTime(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=255), nullable=True),
    sa.Column('cv_score', sa.Integer(), nullable=True),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=True),
    sa.Column('interview_feedback', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('candidate')
    op.drop_table('job')
    # ### end Alembic commands ###
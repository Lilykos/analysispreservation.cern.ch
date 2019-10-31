#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Replace reana with workflows and init table - """

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils

from cap.types import json_type

# revision identifiers, used by Alembic.
revision = 'a85d38b8e3e9'
down_revision = '244808a5da06'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'reana_workflows',
        sa.Column('id',
                  sqlalchemy_utils.types.uuid.UUIDType(),
                  nullable=False),
        sa.Column('rec_uuid',
                  sqlalchemy_utils.types.uuid.UUIDType(),
                  nullable=False),
        sa.Column('cap_user_id', sa.Integer(), nullable=False),
        sa.Column('workflow_id',
                  sqlalchemy_utils.types.uuid.UUIDType(),
                  nullable=False),
        sa.Column('service', sa.Enum('reana', name='service'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('workflow_name', sa.String(length=100), nullable=False),
        sa.Column('name_run', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=100), nullable=False),
        sa.Column('workflow_json',
                  json_type,
                  default=lambda: dict(),
                  nullable=True
                  ),
        sa.Column('logs',
                  json_type,
                  default=lambda: dict(),
                  nullable=True
                  ),
        sa.ForeignKeyConstraint(
            ['cap_user_id'], [u'accounts_user.id'],
            name=op.f('fk_reana_workflows_cap_user_id_accounts_user')),
        sa.ForeignKeyConstraint(
            ['rec_uuid'], [u'records_metadata.id'],
            name=op.f('fk_reana_workflows_rec_uuid_records_metadata')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_reana_workflows')),
        sa.UniqueConstraint('workflow_id',
                            name=op.f('uq_reana_workflows_workflow_id')))
    op.drop_table('reana')
    op.create_unique_constraint(op.f('uq_status_checks_id'), 'status_checks',
                                ['id'])
    # ### end Alembic commands ###


def downgrade():
    """Downgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_status_checks_id'),
                       'status_checks',
                       type_='unique')
    op.create_table(
        'reana',
        sa.Column('id', postgresql.UUID(), autoincrement=False,
                  nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False,
                  nullable=False),
        sa.Column('record_id',
                  postgresql.UUID(),
                  autoincrement=False,
                  nullable=False),
        sa.Column('reana_id',
                  postgresql.UUID(),
                  autoincrement=False,
                  nullable=False),
        sa.Column('name',
                  sa.VARCHAR(length=100),
                  autoincrement=False,
                  nullable=False),
        sa.Column('params',
                  postgresql.JSON(astext_type=sa.Text()),
                  autoincrement=False,
                  nullable=True),
        sa.Column('output',
                  postgresql.JSON(astext_type=sa.Text()),
                  autoincrement=False,
                  nullable=True),
        sa.ForeignKeyConstraint(['record_id'], [u'records_metadata.id'],
                                name=u'fk_reana_record_id_records_metadata'),
        sa.ForeignKeyConstraint(['user_id'], [u'accounts_user.id'],
                                name=u'fk_reana_user_id_accounts_user'),
        sa.PrimaryKeyConstraint('id', name=u'pk_reana'),
        sa.UniqueConstraint('reana_id', name=u'uq_reana_reana_id'))
    op.drop_table('reana_workflows')
    # ### end Alembic commands ###
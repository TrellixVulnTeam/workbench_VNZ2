"""Integrate classification accuracy report

Revision ID: 8cba01b334d7
Revises: 9eae56bc5c8e
Create Date: 2021-08-03 19:50:35.305136

"""

"""
 OpenVINO DL Workbench
 Migration: Integrate classification accuracy report

 Copyright (c) 2021 Intel Corporation

 LEGAL NOTICE: Your use of this software and any required dependent software (the “Software Package”) is subject to
 the terms and conditions of the software license agreements for Software Package, which may also include
 notices, disclaimers, or license terms for third party or open source software
 included in or with the Software Package, and your use indicates your acceptance of all such terms.
 Please refer to the “third-party-programs.txt” or other similarly-named text file included with the Software Package
 for additional details.
 You may obtain a copy of the License at
      https://software.intel.com/content/dam/develop/external/us/en/documents/intel-openvino-license-agreements.pdf
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '8cba01b334d7'
down_revision = '9eae56bc5c8e'
branch_labels = None
depends_on = None


accuracy_report_type_enum = sa.Enum('parent_model_per_tensor', 'parent_model_predictions', 'dataset_annotations',
                                    name='accuracyreporttypeenum')


def upgrade():
    # Drop data and truncate tables for skipping data migration
    op.execute('DELETE FROM accuracy_classification_report_image_classes WHERE id > 0;')
    op.execute('DELETE FROM accuracy_detection_report_image_classes WHERE id > 0;')
    op.execute('DELETE FROM accuracy_report WHERE id > 0;')

    accuracy_report_type_enum.create(op.get_bind(), checkfirst=False)
    op.add_column('accuracy_report', sa.Column('project_id', sa.Integer(), nullable=False))
    op.add_column('accuracy_report', sa.Column('report_type', accuracy_report_type_enum, nullable=False))
    op.create_foreign_key('accuracy_report_project_id_fkey', 'accuracy_report', 'projects', ['project_id'], ['id'])

    # Drop removed columns and its constraints
    op.drop_constraint('accuracy_report_topology_id_fkey', 'accuracy_report', type_='foreignkey')
    op.drop_constraint('accuracy_report_dataset_id_fkey', 'accuracy_report', type_='foreignkey')
    op.drop_constraint('accuracy_report_device_id_fkey', 'accuracy_report', type_='foreignkey')
    op.drop_column('accuracy_report', 'dataset_id')
    op.drop_column('accuracy_report', 'device_id')
    op.drop_column('accuracy_report', 'topology_id')

    # Create corresponding column with report type for accuracy jobs table
    op.add_column('accuracy_jobs', sa.Column('accuracy_report_type', accuracy_report_type_enum, nullable=True))


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('accuracy_report', sa.Column('topology_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('accuracy_report', sa.Column('device_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('accuracy_report', sa.Column('dataset_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint('accuracy_report_project_id_fkey', 'accuracy_report', type_='foreignkey')
    op.create_foreign_key('accuracy_report_device_id_fkey', 'accuracy_report', 'devices', ['device_id'], ['id'])
    op.create_foreign_key('accuracy_report_dataset_id_fkey', 'accuracy_report', 'datasets', ['dataset_id'], ['id'])
    op.create_foreign_key('accuracy_report_topology_id_fkey', 'accuracy_report', 'topologies', ['topology_id'], ['id'])
    op.drop_column('accuracy_report', 'report_type')
    op.drop_column('accuracy_report', 'project_id')
    op.drop_column('accuracy_jobs', 'accuracy_report_type')
    # ### end Alembic commands ###

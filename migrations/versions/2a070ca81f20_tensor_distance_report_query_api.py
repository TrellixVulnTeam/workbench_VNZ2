"""tensor_distance_report_query_api

Revision ID: 2a070ca81f20
Revises: 8cba01b334d7
Create Date: 2021-08-12 14:52:30.635330

"""

"""
 OpenVINO DL Workbench
 Migration: implement tensor distance accuracy report entities query api

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
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a070ca81f20'
down_revision = '8cba01b334d7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DELETE FROM accuracy_classification_report_image_classes WHERE id > 0;')
    op.execute('DELETE FROM accuracy_detection_report_image_classes WHERE id > 0;')
    op.execute('DELETE FROM accuracy_report WHERE id > 0;')

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accuracy_tensor_distance_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('output_names', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['accuracy_report.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('accuracy_tensor_distance_report_image_classes',
    sa.Column('creation_timestamp', sa.DateTime(), nullable=False),
    sa.Column('last_modified', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('report_id', sa.Integer(), nullable=True),
    sa.Column('image_name', sa.String(), nullable=False),
    sa.Column('output_name', sa.String(), nullable=False),
    sa.Column('mse', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['report_id'], ['accuracy_report.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('accuracy_report', 'accuracy_postfix',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('accuracy_report', 'accuracy_result',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.drop_column('per_tensor_report_jobs', 'per_tensor_report')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('per_tensor_report_jobs', sa.Column('per_tensor_report', sa.TEXT(), autoincrement=False, nullable=True))
    op.alter_column('accuracy_report', 'accuracy_result',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('accuracy_report', 'accuracy_postfix',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_table('accuracy_tensor_distance_report_image_classes')
    op.drop_table('accuracy_tensor_distance_report')
    # ### end Alembic commands ###
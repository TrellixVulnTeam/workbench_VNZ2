"""
 OpenVINO DL Workbench
 Class for remote profiling job

 Copyright (c) 2020 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import os
import tarfile
import tempfile
from contextlib import closing

from sqlalchemy.orm import Session

from config.constants import PYTHON_VIRTUAL_ENVIRONMENT_DIR, JOB_SCRIPT_NAME, JOBS_SCRIPTS_FOLDER_NAME, \
    JOB_ARTIFACTS_FOLDER_NAME, JOB_ARTIFACTS_ARCHIVE_NAME
from wb.error.job_error import Int8CalibrationError
from wb.extensions_factories.database import get_db_session_for_celery
from wb.main.console_tool_wrapper.workbench_job_tool import WorkbenchJobTool
from wb.main.enumerates import JobTypesEnum, StatusEnum
from wb.main.jobs.int8_calibration.int8_calibration_job import Int8CalibrationJob
from wb.main.jobs.interfaces.job_observers import Int8CalibrationDBObserver
from wb.main.jobs.mixins.remote_job_mixin import RemoteJobMixin
from wb.main.jobs.utils.utils import collect_artifacts
from wb.main.models import Int8CalibrationJobModel, ProfilingJobModel, TargetModel, ProjectsModel
from wb.main.utils.utils import create_empty_dir


class RemoteInt8CalibrationJob(Int8CalibrationJob, RemoteJobMixin):
    job_type = JobTypesEnum.remote_int8_calibration_type

    def __init__(self, job_id: int, **unused_kwargs):
        super().__init__(job_id=job_id)

        with closing(get_db_session_for_celery()) as session:
            job: Int8CalibrationJobModel = self.get_job_model(session)
            target = job.project.target
        self.openvino_bundle_path = target.bundle_path
        database_observer = Int8CalibrationDBObserver(job_id=self._job_id)
        self._job_state_subject.attach(database_observer)
        self._attach_default_db_and_socket_observers()

    def _clean_paths(self):
        return_code, output = self.clean_remote_paths()
        if return_code:
            message = f'Cannot remove folder {self.job_bundle_path}: {output}'
            raise Int8CalibrationError(message, self._job_id)

    def terminate(self):
        self._job_state_subject.update_state(status=StatusEnum.cancelled)
        return_code, output = self.terminate_remote_process()
        if return_code:
            raise Int8CalibrationError(output, self._job_id)
        self._clean_paths()

    def create_calibration_tool(self, job: Int8CalibrationJobModel) -> WorkbenchJobTool:
        job_script_path = os.path.join(self.job_bundle_path, JOBS_SCRIPTS_FOLDER_NAME, JOB_SCRIPT_NAME)
        target: ProjectsModel = job.project.target
        venv_path = os.path.join(target.bundle_path, PYTHON_VIRTUAL_ENVIRONMENT_DIR)
        return WorkbenchJobTool(job_script_path=job_script_path,
                                openvino_package_root_path=target.bundle_path,
                                job_bundle_path=self.job_bundle_path, venv_path=venv_path)

    def get_openvino_bundle_path(self, session: Session) -> str:
        job: ProfilingJobModel = self.get_job_model(session)
        target: TargetModel = job.project.target
        return target.bundle_path

    def collect_artifacts(self):
        with closing(get_db_session_for_celery()) as session:
            job_model: Int8CalibrationJobModel = self.get_job_model(session)
            target = job_model.project.target
            dest_archive = os.path.join(self.job_bundle_path, JOB_ARTIFACTS_FOLDER_NAME, JOB_ARTIFACTS_ARCHIVE_NAME)
            with tempfile.TemporaryDirectory('rw') as tmp_folder:
                result_archive = os.path.join(tmp_folder, JOB_ARTIFACTS_ARCHIVE_NAME)
                collect_artifacts(target.id, dest_archive, result_archive, session)
                with tarfile.open(result_archive, 'r:gz') as tar:
                    def is_within_directory(directory, target):
                        
                        abs_directory = os.path.abspath(directory)
                        abs_target = os.path.abspath(target)
                    
                        prefix = os.path.commonprefix([abs_directory, abs_target])
                        
                        return prefix == abs_directory
                    
                    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    
                        for member in tar.getmembers():
                            member_path = os.path.join(path, member.name)
                            if not is_within_directory(path, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                    
                        tar.extractall(path, members, numeric_owner=numeric_owner) 
                        
                    
                    safe_extract(tar, path=tmp_folder)
                create_empty_dir(job_model.result_model.path)
                self.move_optimized_model(tmp_folder, job_model.result_model.path, self.job_id)
        self._clean_paths()

import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

from app.models.job import JobCreate, JobStatus, JobUpdate
from app.models.project import ProjectCreate
from app.routers.jobs import get_job as get_job_route
from app.services import job_service, project_service
from app.storage import job_store, project_store


class JobServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._original_projects_dir = project_store.PROJECTS_DIR
        self._original_job_projects_dir = job_store.PROJECTS_DIR
        project_store.PROJECTS_DIR = Path(self._tmpdir.name)
        job_store.PROJECTS_DIR = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        project_store.PROJECTS_DIR = self._original_projects_dir
        job_store.PROJECTS_DIR = self._original_job_projects_dir
        self._tmpdir.cleanup()

    def test_create_job_records_job_id_on_project(self) -> None:
        project = project_service.create_project(ProjectCreate(title="Project One"))

        job = job_service.create_job(JobCreate(type="lyrics_generation", projectId=project.id))
        loaded_project = project_service.get_project(project.id)

        self.assertIsNotNone(job)
        self.assertEqual(job.status, JobStatus.queued)
        self.assertIn(job.id, loaded_project.assets.jobIds)

    def test_update_job_appends_log_and_changes_status(self) -> None:
        project = project_service.create_project(ProjectCreate(title="Project Two"))
        job = job_service.create_job(JobCreate(type="music_generation", projectId=project.id))

        updated = job_service.update_job(
            job.id,
            JobUpdate(status=JobStatus.running, progress=0.5, message="halfway there"),
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, JobStatus.running)
        self.assertEqual(updated.progress, 0.5)
        self.assertEqual(updated.log[-1].message, "halfway there")

    def test_jobs_route_raises_404_for_missing_job(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            get_job_route("missing-job")

        self.assertEqual(ctx.exception.status_code, 404)

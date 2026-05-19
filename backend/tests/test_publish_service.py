import tempfile
import unittest
from pathlib import Path

from app.models.project import ProjectCreate
from app.services import lyric_service, publish_service, project_service
from app.storage import job_store, project_store


class PublishServiceTests(unittest.TestCase):
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

    def test_generate_publish_info_writes_metadata_and_returns_copy(self) -> None:
        project = project_service.create_project(ProjectCreate(title="Publish Project", theme="night", language="en"))
        lyric_service.save_lyrics(project.id, "first line\nsecond line", "manual edit")

        response = publish_service.generate_publish_info(project.id, "My Title")

        self.assertIn("My Title", response.titleCandidates[0])
        self.assertTrue((project_store.PROJECTS_DIR / project.id / "metadata" / "publish_info.json").exists())
        self.assertGreater(len(response.checklist), 0)


import tempfile
import unittest
from pathlib import Path

from app.models.project import ProjectCreate
from app.services import lrc_service, lyric_service, project_service
from app.storage import job_store, project_store


class LrcServiceTests(unittest.TestCase):
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

    def test_generate_lrc_creates_draft_from_lyrics(self) -> None:
        project = project_service.create_project(ProjectCreate(title="LRC Project"))
        lyric_service.save_lyrics(project.id, "first line\nsecond line", "manual edit")

        record = lrc_service.generate_lrc(project.id, None, "draft")
        loaded = project_service.get_project(project.id)

        self.assertEqual(record.id, "lrc_v1")
        self.assertEqual(loaded.selectedLrcFile, "lrc_v1")
        self.assertTrue((project_store.PROJECTS_DIR / record.path).exists())

    def test_save_lrc_records_manual_edit(self) -> None:
        project = project_service.create_project(ProjectCreate(title="LRC Project 2"))

        record = lrc_service.save_lrc(project.id, "[00:00.00] hello", None, "manual_edit")
        loaded = project_service.get_project(project.id)

        self.assertEqual(record.id, "lrc_v1")
        self.assertEqual(loaded.selectedLrcFile, "lrc_v1")
        self.assertEqual(len(loaded.assets.lrcFiles), 1)


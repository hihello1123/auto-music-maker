import tempfile
import unittest
from pathlib import Path

from app.models.project import ProjectCreate
from app.services import file_service, project_service
from app.storage import job_store, project_store


class FileServiceTests(unittest.TestCase):
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

    def test_upload_vocal_creates_safe_filename_and_project_record(self) -> None:
        project = project_service.create_project(ProjectCreate(title="File Project"))

        record = file_service.upload_vocal(project.id, "My Vocal Take.MP3", b"fake mp3 bytes")
        loaded = project_service.get_project(project.id)

        self.assertTrue(record.filename.endswith(".mp3"))
        self.assertEqual(record.originalFilename, "My Vocal Take.MP3")
        self.assertEqual(len(loaded.assets.vocalFiles), 1)
        self.assertTrue((project_store.PROJECTS_DIR / record.path).exists())

    def test_upload_vocal_rejects_unsupported_extension(self) -> None:
        project = project_service.create_project(ProjectCreate(title="File Project 2"))

        with self.assertRaises(ValueError):
            file_service.upload_vocal(project.id, "bad.txt", b"x")


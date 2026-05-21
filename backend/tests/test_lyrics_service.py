import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models.lyrics import LyricsGenerateRequest, LyricsSaveRequest
from app.models.project import ProjectCreate
from app.services import lyric_service, project_service
from app.storage import job_store, project_store


class LyricsServiceTests(unittest.TestCase):
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

    def test_save_lyrics_creates_versioned_file_and_updates_project(self) -> None:
        project = project_service.create_project(ProjectCreate(title="Lyric Project"))

        asset = lyric_service.save_lyrics(project.id, "line one\nline two", "내가 적은 라벨")
        loaded = project_service.get_project(project.id)

        self.assertEqual(asset.id, "lyrics_v1")
        self.assertEqual(asset.label, "내가 적은 라벨")
        self.assertEqual(loaded.selectedLyricsVersion, "lyrics_v1")
        self.assertEqual(len(loaded.assets.lyricsVersions), 1)
        self.assertTrue((project_store.PROJECTS_DIR / project.id / "lyrics" / "lyrics_v1.md").exists())
        self.assertEqual(loaded.assets.lyricsVersions[0].label, "내가 적은 라벨")

    @patch("app.services.ollama_service.generate_lyrics", return_value="Verse 1\nChorus")
    def test_generate_lyrics_uses_ollama_and_updates_project(self, mock_generate) -> None:
        project = project_service.create_project(ProjectCreate(title="Generated Lyric Project"))

        asset = lyric_service.generate_lyrics(
            project.id,
            LyricsGenerateRequest(model="lyricist-qwen", theme="rain", language="en", style="soft", instruction="short lines"),
        )
        loaded = project_service.get_project(project.id)

        self.assertEqual(mock_generate.call_count, 1)
        self.assertEqual(asset.id, "lyrics_v1")
        self.assertEqual(loaded.selectedLyricsVersion, "lyrics_v1")
        self.assertEqual(loaded.assets.lyricsVersions[0].filename, "lyrics_v1.md")

import unittest
from datetime import datetime

from app.models.project import Project, ProjectAssetRecord


class ProjectModelTests(unittest.TestCase):
    def test_project_assets_default_to_empty_collections(self) -> None:
        project = Project(id="p1", title="Test Project")

        self.assertEqual(project.assets.lyricsVersions, [])
        self.assertEqual(project.assets.vocalFiles, [])
        self.assertEqual(project.assets.audioFiles, [])
        self.assertEqual(project.assets.lrcFiles, [])
        self.assertEqual(project.assets.videoFiles, [])
        self.assertEqual(project.assets.jobIds, [])

    def test_project_asset_record_serializes_with_required_fields(self) -> None:
        record = ProjectAssetRecord(
            id="lyrics_v1",
            label="initial",
            filename="lyrics_v1.md",
            path="data/projects/p1/lyrics/lyrics_v1.md",
            metadataPath="data/projects/p1/metadata/lyrics_v1.json",
        )

        payload = record.model_dump()

        self.assertEqual(payload["id"], "lyrics_v1")
        self.assertEqual(payload["filename"], "lyrics_v1.md")
        self.assertEqual(payload["path"], "data/projects/p1/lyrics/lyrics_v1.md")
        self.assertIsInstance(payload["createdAt"], datetime)


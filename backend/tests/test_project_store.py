import tempfile
import unittest
from pathlib import Path

from app.models.project import Project, ProjectAssetRecord, ProjectAssets
from app.storage import project_store


class ProjectStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._original_dir = project_store.PROJECTS_DIR
        project_store.PROJECTS_DIR = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        project_store.PROJECTS_DIR = self._original_dir
        self._tmpdir.cleanup()

    def test_save_and_load_project_round_trip(self) -> None:
        project = Project(
            id="p1",
            title="Still In The Rain",
            theme="night",
            genre="emotional pop ballad",
            assets=ProjectAssets(
                lyricsVersions=[
                    ProjectAssetRecord(
                        id="lyrics_v1",
                        label="draft",
                        filename="lyrics_v1.md",
                        path="data/projects/p1/lyrics/lyrics_v1.md",
                    )
                ],
                jobIds=["job_001"],
            ),
        )

        project_store.save_project(project)
        loaded = project_store.get_project("p1")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Still In The Rain")
        self.assertEqual(loaded.assets.lyricsVersions[0].id, "lyrics_v1")
        self.assertEqual(loaded.assets.jobIds, ["job_001"])

    def test_list_projects_returns_all_saved_projects(self) -> None:
        first = Project(id="p1", title="One")
        second = Project(id="p2", title="Two")

        project_store.save_project(first)
        project_store.save_project(second)

        projects = project_store.list_projects()

        self.assertEqual({project.id for project in projects}, {"p1", "p2"})


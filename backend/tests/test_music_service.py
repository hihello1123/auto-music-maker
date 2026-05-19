import tempfile
import unittest
from pathlib import Path
import math
import struct
import wave

from app.models.job import JobStatus
from app.models.music import MusicGenerateRequest
from app.models.project import ProjectCreate
from app.services import job_service, lyric_service, music_plan_service, music_service, project_service
from app.storage import job_store, project_store


class MusicServiceTests(unittest.TestCase):
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

    def _prepare_project_with_lyrics(self):
        project = project_service.create_project(ProjectCreate(title="Music Project", theme="rain"))
        lyric_service.save_lyrics(project.id, "line one\nline two", "manual edit")
        return project_service.get_project(project.id)

    def test_generate_music_records_prompt_and_job(self) -> None:
        project = self._prepare_project_with_lyrics()
        original_has_api = music_service.ace_step_service.has_configured_api
        original_plan_has_api = music_plan_service.ace_step_service.has_configured_api

        try:
            music_service.ace_step_service.has_configured_api = lambda: False
            music_plan_service.ace_step_service.has_configured_api = lambda: False

            response = music_service.generate_music(
                project.id,
                MusicGenerateRequest(
                    mode="lyrics_only",
                    duration=60,
                    seed=1234,
                    count=3,
                    genre="ballad",
                    bpm=85,
                    key="C minor",
                ),
            )
            loaded_job = job_service.get_job(response.jobId)
            loaded_project = project_service.get_project(project.id)
        finally:
            music_service.ace_step_service.has_configured_api = original_has_api
            music_plan_service.ace_step_service.has_configured_api = original_plan_has_api

        self.assertEqual(response.mode, "lyrics_only")
        self.assertEqual(response.seed, 1234)
        self.assertEqual(response.promptFileId, "ace_step_prompt_001")
        self.assertEqual(response.musicPlanFileId, "music_plan_001")
        self.assertEqual(response.promptPresetId, "emotional_pop_ballad")
        self.assertEqual(response.engine, "placeholder")
        self.assertEqual(loaded_job.status, JobStatus.completed)
        self.assertEqual(loaded_job.result["status"], "completed")
        self.assertEqual(len(loaded_project.assets.promptFiles), 1)
        self.assertEqual(len(loaded_project.assets.musicPlans), 1)
        self.assertEqual(len(loaded_project.assets.audioFiles), 3)
        self.assertIsNotNone(loaded_project.selectedAudioFile)
        self.assertEqual(loaded_project.selectedPromptPreset, "emotional_pop_ballad")
        self.assertIsNotNone(loaded_project.selectedMusicPlan)
        self.assertTrue((project_store.PROJECTS_DIR / loaded_project.assets.audioFiles[0].path).exists())

    def test_generate_music_plan_records_music_plan_asset(self) -> None:
        project = self._prepare_project_with_lyrics()
        original_has_api = music_plan_service.ace_step_service.has_configured_api

        try:
            music_plan_service.ace_step_service.has_configured_api = lambda: False
            plan = music_plan_service.generate_music_plan(
                project.id,
                MusicGenerateRequest(
                    mode="lyrics_only",
                    duration=60,
                    seed=1234,
                    count=1,
                    genre="ballad",
                    bpm=85,
                    key="C minor",
                ),
            )
            loaded_project = project_service.get_project(project.id)
        finally:
            music_plan_service.ace_step_service.has_configured_api = original_has_api

        self.assertEqual(plan.musicPlanFileId, "music_plan_001")
        self.assertEqual(plan.promptPresetId, "emotional_pop_ballad")
        self.assertEqual(plan.engine, "local-fallback")
        self.assertEqual(len(loaded_project.assets.musicPlans), 1)
        self.assertEqual(loaded_project.selectedPromptPreset, "emotional_pop_ballad")
        self.assertEqual(loaded_project.selectedMusicPlan, "music_plan_001")

    def test_generate_music_uses_configured_ace_step_runner(self) -> None:
        project = self._prepare_project_with_lyrics()

        original_has_runner = music_service.ace_step_service.has_configured_runner
        original_has_api = music_service.ace_step_service.has_configured_api
        original_plan_has_api = music_plan_service.ace_step_service.has_configured_api
        original_build_command = music_service.ace_step_service.build_command
        original_execute_runner = music_service.ace_step_service.execute_runner

        def fake_execute_runner(command, cwd=None):
            output_dir = None
            for index, token in enumerate(command):
                if token == "--output-dir":
                    output_dir = Path(command[index + 1])
                    break
            assert output_dir is not None
            output_dir.mkdir(parents=True, exist_ok=True)
            sample_rate = 44100
            for idx in range(2):
                wav_path = output_dir / f"rendered_{idx + 1}.wav"
                with wave.open(str(wav_path), "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    frames = bytearray()
                    for i in range(sample_rate):
                        sample = int(12000 * math.sin(2 * math.pi * (220 + (idx * 20)) * (i / sample_rate)))
                        frames.extend(struct.pack("<h", sample))
                    wav_file.writeframes(bytes(frames))

        try:
            music_service.ace_step_service.has_configured_api = lambda: False
            music_service.ace_step_service.has_configured_runner = lambda: True
            music_plan_service.ace_step_service.has_configured_api = lambda: False
            music_service.ace_step_service.build_command = lambda *, prompt_file, output_dir, request_data: [
                "ace-step",
                "--prompt",
                str(prompt_file),
                "--output-dir",
                str(output_dir),
                "--seed",
                str(request_data.seed or ""),
            ]
            music_service.ace_step_service.execute_runner = fake_execute_runner

            response = music_service.generate_music(
                project.id,
                MusicGenerateRequest(
                    mode="lyrics_only",
                    duration=2,
                    seed=7,
                    count=2,
                    genre="ballad",
                    bpm=90,
                    key="D major",
                ),
            )
            loaded_job = job_service.get_job(response.jobId)
            loaded_project = project_service.get_project(project.id)
        finally:
            music_service.ace_step_service.has_configured_api = original_has_api
            music_service.ace_step_service.has_configured_runner = original_has_runner
            music_plan_service.ace_step_service.has_configured_api = original_plan_has_api
            music_service.ace_step_service.build_command = original_build_command
            music_service.ace_step_service.execute_runner = original_execute_runner

        self.assertEqual(response.engine, "ace-step-cli")
        self.assertEqual(response.musicPlanFileId, "music_plan_001")
        self.assertEqual(response.promptPresetId, "emotional_pop_ballad")
        self.assertEqual(len(response.audioFileIds), 2)
        self.assertEqual(loaded_job.status, JobStatus.completed)
        self.assertEqual(loaded_job.result["engine"], "ace-step-cli")
        self.assertEqual(loaded_job.result["musicPlanFileId"], "music_plan_001")
        self.assertEqual(loaded_job.result["promptPresetId"], "emotional_pop_ballad")
        self.assertEqual(len(loaded_project.assets.audioFiles), 2)
        self.assertEqual(len(loaded_project.assets.musicPlans), 1)

    def test_generate_music_uses_configured_ace_step_api(self) -> None:
        project = self._prepare_project_with_lyrics()

        original_has_api = music_service.ace_step_service.has_configured_api
        original_has_runner = music_service.ace_step_service.has_configured_runner
        original_plan_has_api = music_plan_service.ace_step_service.has_configured_api
        original_plan_generate = music_plan_service.ace_step_service.generate_music_blueprint
        original_submit = music_service.ace_step_service.submit_generation_task
        original_poll = music_service.ace_step_service.poll_generation_task
        original_extract = music_service.ace_step_service.extract_audio_urls
        original_download = music_service.ace_step_service.download_audio_url

        def fake_download_audio_url(audio_url, destination):
            sample_rate = 44100
            with wave.open(str(destination), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                frames = bytearray()
                for i in range(sample_rate):
                    sample = int(12000 * math.sin(2 * math.pi * 440 * (i / sample_rate)))
                    frames.extend(struct.pack("<h", sample))
                wav_file.writeframes(bytes(frames))

        try:
            music_service.ace_step_service.has_configured_api = lambda: True
            music_service.ace_step_service.has_configured_runner = lambda: False
            music_plan_service.ace_step_service.has_configured_api = lambda: True
            music_plan_service.ace_step_service.generate_music_blueprint = lambda **_kwargs: {
                "caption": "blueprint-caption",
                "lyrics": "blueprint-lyrics",
                "bpm": 88,
                "key_scale": "A minor",
                "duration": 2,
                "time_signature": "4/4",
                "vocal_language": "en",
            }
            music_service.ace_step_service.submit_generation_task = lambda *, prompt, lyrics, request_data, music_plan=None: "task-123"
            music_service.ace_step_service.poll_generation_task = lambda task_id: {"status": 1, "result": "[{\"file\": \"/v1/audio?path=/tmp/output.wav\"}]"}
            music_service.ace_step_service.extract_audio_urls = lambda task_result: ["/v1/audio?path=/tmp/output.wav"]
            music_service.ace_step_service.download_audio_url = fake_download_audio_url

            response = music_service.generate_music(
                project.id,
                MusicGenerateRequest(
                    mode="lyrics_only",
                    duration=2,
                    seed=9,
                    count=1,
                    genre="ballad",
                    bpm=88,
                    key="A minor",
                ),
            )
            loaded_job = job_service.get_job(response.jobId)
            loaded_project = project_service.get_project(project.id)
        finally:
            music_service.ace_step_service.has_configured_api = original_has_api
            music_service.ace_step_service.has_configured_runner = original_has_runner
            music_plan_service.ace_step_service.has_configured_api = original_plan_has_api
            music_plan_service.ace_step_service.generate_music_blueprint = original_plan_generate
            music_service.ace_step_service.submit_generation_task = original_submit
            music_service.ace_step_service.poll_generation_task = original_poll
            music_service.ace_step_service.extract_audio_urls = original_extract
            music_service.ace_step_service.download_audio_url = original_download

        self.assertEqual(response.engine, "ace-step-api")
        self.assertEqual(response.musicPlanFileId, "music_plan_001")
        self.assertEqual(response.promptPresetId, "emotional_pop_ballad")
        self.assertEqual(len(response.audioFileIds), 1)
        self.assertEqual(loaded_job.status, JobStatus.completed)
        self.assertEqual(loaded_job.result["engine"], "ace-step-api")
        self.assertEqual(loaded_job.result["musicPlanFileId"], "music_plan_001")
        self.assertEqual(loaded_job.result["promptPresetId"], "emotional_pop_ballad")
        self.assertEqual(len(loaded_project.assets.audioFiles), 1)
        self.assertEqual(len(loaded_project.assets.musicPlans), 1)

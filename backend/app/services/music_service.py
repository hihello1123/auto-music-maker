import io
import math
import struct
from datetime import datetime
import wave

from app.models.job import JobCreate, JobUpdate
from app.models.music import MusicGenerateRequest, MusicGenerateResponse
import app.services.music_plan_service as music_plan_service
import app.services.prompt_preset_service as prompt_preset_service
import app.services.ace_step_service as ace_step_service
import app.services.file_service as file_service
import app.services.job_service as job_service
from app.storage import project_store


def _generate_placeholder_wav(duration_seconds: int, frequency_hz: int) -> bytes:
    sample_rate = 44100
    amplitude = 16000
    frames = bytearray()
    total_samples = max(1, duration_seconds) * sample_rate
    for i in range(total_samples):
        sample = int(amplitude * math.sin(2 * math.pi * frequency_hz * (i / sample_rate)))
        frames.extend(struct.pack("<h", sample))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))
    return buffer.getvalue()


def _ace_step_output_dir(project_id: str, job_id: str):
    return project_store.PROJECTS_DIR / project_id / "audio" / "ace_step_runs" / job_id


def generate_music(project_id: str, request_data: MusicGenerateRequest) -> MusicGenerateResponse:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    job = job_service.create_job(JobCreate(type="music_generation", projectId=project_id))
    try:
        music_plan = music_plan_service.generate_music_plan(project_id, request_data)
        lyrics_content = music_plan.lyrics
        prompt_request = request_data.model_copy(
            update={
                "genre": music_plan.genre or request_data.genre,
                "bpm": music_plan.bpm if music_plan.bpm is not None else request_data.bpm,
                "key": music_plan.key or request_data.key,
                "duration": music_plan.duration if music_plan.duration is not None else request_data.duration,
                "songStructure": request_data.songStructure,
            }
        )
        prompt = ace_step_service.build_prompt(
            lyrics_content=lyrics_content,
            request_data=prompt_request,
            project_title=project.title,
            project_theme=project.theme,
            prompt_preset=prompt_preset_service.resolve_prompt_preset(
                genre=music_plan.genre or request_data.genre or project.genre,
                preset_id=music_plan.promptPresetId or request_data.promptPresetId or project.selectedPromptPreset,
            ),
        )
        prompt_asset = file_service.add_prompt_asset(project_id, "ace_step_prompt", prompt)
        audio_assets = []
        prompt_path = project_store.PROJECTS_DIR / (prompt_asset.path or "")
        engine = "placeholder"
        message = "Placeholder wav generated locally; ACE-Step execution is not wired yet."

        if ace_step_service.has_configured_api():
            output_dir = project_store.PROJECTS_DIR / project_id / "audio" / "ace_step_runs" / job.id
            output_dir.mkdir(parents=True, exist_ok=True)
            task_id = ace_step_service.submit_generation_task(
                prompt=prompt,
                lyrics=lyrics_content,
                request_data=request_data,
                music_plan=music_plan.model_dump(),
            )
            task_result = ace_step_service.poll_generation_task(task_id)
            if task_result.get("status") == 2:
                raise RuntimeError(f"ACE-Step task failed: {task_result}")

            audio_urls = ace_step_service.extract_audio_urls(task_result)
            if not audio_urls:
                raise RuntimeError(f"ACE-Step task finished but returned no audio files: {task_result}")

            for index, audio_url in enumerate(audio_urls[: max(1, request_data.count)]):
                destination = output_dir / f"generated_{index + 1:03d}.wav"
                ace_step_service.download_audio_url(audio_url, destination)
                audio_assets.append(file_service.add_audio_asset_from_path(project_id, destination, asset_prefix="generated"))
            engine = "ace-step-api"
            status = "completed"
            message = "ACE-Step API generated audio files and they were imported."
        elif ace_step_service.has_configured_runner():
            output_dir = _ace_step_output_dir(project_id, job.id)
            output_dir.mkdir(parents=True, exist_ok=True)
            command = ace_step_service.build_command(
                prompt_file=prompt_path,
                output_dir=output_dir,
                request_data=request_data,
            )
            ace_step_service.execute_runner(command, cwd=project_store.PROJECTS_DIR / project_id)

            wav_files = sorted(output_dir.rglob("*.wav"))
            if not wav_files:
                raise RuntimeError(f"ACE-Step command finished but produced no wav files in {output_dir}")

            for wav_path in wav_files[: max(1, request_data.count)]:
                audio_assets.append(file_service.add_audio_asset_from_path(project_id, wav_path, asset_prefix="generated"))
            engine = "ace-step-cli"
            status = "completed"
            message = "ACE-Step command executed and audio files imported."
        else:
            frequency_seed = request_data.seed or 220
            for index in range(max(1, request_data.count)):
                frequency = frequency_seed + (index * 30)
                wav_bytes = _generate_placeholder_wav(request_data.duration, frequency)
                audio_asset = file_service.add_audio_asset(
                    project_id,
                    asset_prefix="generated",
                    content=wav_bytes,
                    original_filename=f"generated_{index + 1:03d}.wav",
                )
                audio_assets.append(audio_asset)
            engine = "placeholder"
            status = "completed"

        job_service.update_job(
            job.id,
            JobUpdate(
                result={
                    "mode": request_data.mode,
                    "lyricsVersion": request_data.lyricsVersion or project.selectedLyricsVersion,
                    "seed": request_data.seed,
                    "promptFileId": prompt_asset.id,
                    "musicPlanFileId": music_plan.musicPlanFileId,
                    "promptPresetId": music_plan.promptPresetId,
                    "audioFileIds": [asset.id for asset in audio_assets],
                    "status": "completed",
                    "engine": engine,
                    "musicPlanEngine": music_plan.engine,
                },
                status=status,
                progress=1.0,
                message=message,
            ),
        )

        return MusicGenerateResponse(
            jobId=job.id,
            prompt=prompt,
            mode=request_data.mode,
            seed=request_data.seed,
            promptFileId=prompt_asset.id,
            musicPlanFileId=music_plan.musicPlanFileId,
            promptPresetId=music_plan.promptPresetId,
            audioFileIds=[asset.id for asset in audio_assets],
            engine=engine,
            createdAt=datetime.now(),
        )
    except Exception as exc:
        job_service.update_job(
            job.id,
            JobUpdate(
                status="failed",
                progress=1.0,
                message=str(exc),
                error=str(exc),
            ),
        )
        raise

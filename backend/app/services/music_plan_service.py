from datetime import datetime

from app.models.music import MusicGenerateRequest, MusicPlanResponse
import app.services.prompt_preset_service as prompt_preset_service
import app.services.ace_step_service as ace_step_service
import app.services.file_service as file_service
from app.storage import project_store


def _lyrics_content_from_project(project_id: str, lyrics_version: str | None) -> str:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    target_version = lyrics_version or project.selectedLyricsVersion
    if not target_version:
        raise ValueError("No lyrics version selected for this project")

    for record in project.assets.lyricsVersions:
        if record.id == target_version and record.path:
            content_path = project_store.PROJECTS_DIR / record.path
            if not content_path.exists():
                raise ValueError(f"Lyrics file {record.path} not found")
            return content_path.read_text(encoding="utf-8")

    raise ValueError(f"Lyrics version {target_version} not found")


def _fallback_blueprint(
    *,
    source_prompt: str,
    lyrics_content: str,
    request_data: MusicGenerateRequest,
    prompt_preset_id: str | None = None,
    prompt_preset_label: str | None = None,
) -> MusicPlanResponse:
    return MusicPlanResponse(
        promptPresetId=prompt_preset_id,
        promptPresetLabel=prompt_preset_label,
        sourcePrompt=source_prompt,
        caption=source_prompt,
        lyrics=lyrics_content.strip(),
        genre=request_data.genre,
        bpm=request_data.bpm,
        key=request_data.key,
        duration=request_data.duration,
        timeSignature="4/4",
        language="en",
        engine="local-fallback",
        createdAt=datetime.now(),
    )


def generate_music_plan(project_id: str, request_data: MusicGenerateRequest) -> MusicPlanResponse:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    lyrics_content = _lyrics_content_from_project(project_id, request_data.lyricsVersion)
    effective_genre = request_data.genre or project.genre
    effective_bpm = request_data.bpm if request_data.bpm is not None else project.bpm
    effective_key = request_data.key or project.key
    project_language = project.language or "en"
    prompt_preset = prompt_preset_service.resolve_prompt_preset(
        genre=effective_genre,
        preset_id=request_data.promptPresetId or project.selectedPromptPreset,
    )
    effective_bpm = effective_bpm if effective_bpm is not None else prompt_preset.defaultBpm
    effective_key = effective_key or prompt_preset.defaultKey
    effective_duration = request_data.duration if request_data.duration else (prompt_preset.defaultDuration or 60)
    source_prompt = ace_step_service.build_blueprint_prompt(
        lyrics_content=lyrics_content,
        request_data=request_data.model_copy(
            update={
                "genre": effective_genre,
                "bpm": effective_bpm,
                "key": effective_key,
                "duration": effective_duration,
            }
        ),
        project_title=project.title,
        project_theme=project.theme,
        prompt_preset=prompt_preset,
    )

    plan = None
    if ace_step_service.has_configured_api():
        try:
            blueprint_data = ace_step_service.generate_music_blueprint(
                prompt=source_prompt,
                lyrics=lyrics_content,
                request_data=request_data,
            )
            plan = MusicPlanResponse(
                promptPresetId=prompt_preset.id,
                promptPresetLabel=prompt_preset.label,
                sourcePrompt=source_prompt,
                caption=str(blueprint_data.get("caption") or source_prompt).strip(),
                lyrics=str(blueprint_data.get("lyrics") or lyrics_content).strip(),
                genre=effective_genre,
                bpm=blueprint_data.get("bpm") if blueprint_data.get("bpm") is not None else effective_bpm,
                key=(blueprint_data.get("key_scale") or blueprint_data.get("key") or effective_key),
                duration=blueprint_data.get("duration") if blueprint_data.get("duration") is not None else effective_duration,
                timeSignature=(blueprint_data.get("time_signature") or blueprint_data.get("timesignature") or "4/4"),
                language=str(blueprint_data.get("vocal_language") or project_language or "en"),
                engine="ace-step-lm",
                createdAt=datetime.now(),
            )
        except Exception:
            plan = None

    if plan is None:
        plan = _fallback_blueprint(
            source_prompt=source_prompt,
            lyrics_content=lyrics_content,
            request_data=request_data,
            prompt_preset_id=prompt_preset.id,
            prompt_preset_label=prompt_preset.label,
        )
        plan.genre = effective_genre
        plan.bpm = effective_bpm
        plan.key = effective_key
        plan.language = project_language
        plan.duration = effective_duration

    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    asset_record = file_service.add_json_asset(
        project_id=project_id,
        collection_name="music_plans",
        asset_collection_name="musicPlans",
        asset_prefix="music_plan",
        content=plan.model_dump(),
    )
    updated = project_store.get_project(project_id)
    if not updated:
        raise ValueError(f"Project {project_id} not found")
    updated.selectedPromptPreset = prompt_preset.id
    updated.selectedMusicPlan = asset_record.id
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    plan.musicPlanFileId = asset_record.id
    return plan

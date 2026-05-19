import json
import re
from datetime import datetime
from pathlib import Path

from app.models.lyrics import LyricsVersionRecord
from app.models.project import ProjectAssetRecord
import app.services.ollama_service as ollama_service
import app.services.project_service as project_service
from app.storage import project_store

LYRICS_DIR_NAME = "lyrics"
METADATA_DIR_NAME = "metadata"


def _project_dir(project_id: str) -> Path:
    return project_store.PROJECTS_DIR / project_id


def _lyrics_dir(project_id: str) -> Path:
    return _project_dir(project_id) / LYRICS_DIR_NAME


def _metadata_dir(project_id: str) -> Path:
    return _project_dir(project_id) / METADATA_DIR_NAME


def _next_version(project_id: str) -> int:
    project = project_store.get_project(project_id)
    if not project:
        return 1
    return len(project.assets.lyricsVersions) + 1


def _safe_label(label: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", label.strip().lower()).strip("_")
    return slug or "lyrics"


def _write_version_files(project_id: str, content: str, label: str) -> LyricsVersionRecord:
    version_number = _next_version(project_id)
    version = f"lyrics_v{version_number}"
    safe_label = _safe_label(label)
    lyrics_dir = _lyrics_dir(project_id)
    metadata_dir = _metadata_dir(project_id)
    lyrics_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{version}.md"
    content_path = lyrics_dir / filename
    metadata_path = metadata_dir / f"{version}.json"
    created_at = datetime.now()

    content_path.write_text(content, encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "version": version,
                "label": safe_label,
                "filename": filename,
                "createdAt": created_at.isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return LyricsVersionRecord(
        version=version,
        label=safe_label,
        filename=filename,
        contentPath=str(content_path.relative_to(project_store.PROJECTS_DIR)),
        metadataPath=str(metadata_path.relative_to(project_store.PROJECTS_DIR)),
        createdAt=created_at,
    )


def generate_lyrics(project_id: str, request_data) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    content = ollama_service.generate_lyrics(
        model=request_data.model,
        theme=request_data.theme or project.theme,
        language=request_data.language or project.language,
        style=request_data.style or project.genre,
        instruction=request_data.instruction,
        version_count=request_data.versionCount,
    )
    version_record = _write_version_files(project_id, content, label="generated")
    asset_record = ProjectAssetRecord(
        id=version_record.version,
        label=version_record.label,
        filename=version_record.filename,
        path=version_record.contentPath,
        metadataPath=version_record.metadataPath,
        createdAt=version_record.createdAt,
        updatedAt=version_record.createdAt,
    )
    project_service.add_project_asset(project_id, "lyricsVersions", asset_record)
    updated = project_store.get_project(project_id)
    updated.selectedLyricsVersion = version_record.version
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return asset_record


def save_lyrics(project_id: str, content: str, label: str) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    version_record = _write_version_files(project_id, content, label=label)
    asset_record = ProjectAssetRecord(
        id=version_record.version,
        label=version_record.label,
        filename=version_record.filename,
        path=version_record.contentPath,
        metadataPath=version_record.metadataPath,
        createdAt=version_record.createdAt,
        updatedAt=version_record.createdAt,
    )
    project_service.add_project_asset(project_id, "lyricsVersions", asset_record)
    updated = project_store.get_project(project_id)
    updated.selectedLyricsVersion = version_record.version
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return asset_record

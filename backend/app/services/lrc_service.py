import json
from datetime import datetime, timedelta
from pathlib import Path

from app.models.lrc import LrcVersionRecord
from app.models.project import ProjectAssetRecord
from app.services import file_service, project_service
from app.storage import project_store

LRC_DIR_NAME = "lrc"
METADATA_DIR_NAME = "metadata"


def _project_dir(project_id: str) -> Path:
    return project_store.PROJECTS_DIR / project_id


def _lrc_dir(project_id: str) -> Path:
    return _project_dir(project_id) / LRC_DIR_NAME


def _metadata_dir(project_id: str) -> Path:
    return _project_dir(project_id) / METADATA_DIR_NAME


def _next_version(project_id: str) -> int:
    project = project_store.get_project(project_id)
    if not project:
        return 1
    return len(project.assets.lrcFiles) + 1


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


def _draft_lrc_from_lyrics(lyrics_content: str) -> str:
    lines = [line.strip() for line in lyrics_content.splitlines() if line.strip()]
    if not lines:
        return "[00:00.00] "

    output: list[str] = []
    current = timedelta(seconds=0)
    step = timedelta(seconds=4)
    for line in lines:
        minutes, seconds = divmod(int(current.total_seconds()), 60)
        output.append(f"[{minutes:02d}:{seconds:02d}.00] {line}")
        current += step
    return "\n".join(output)


def _write_lrc_files(project_id: str, content: str, label: str) -> LrcVersionRecord:
    version_number = _next_version(project_id)
    version = f"lrc_v{version_number}"
    lrc_dir = _lrc_dir(project_id)
    metadata_dir = _metadata_dir(project_id)
    lrc_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{version}.lrc"
    content_path = lrc_dir / filename
    metadata_path = metadata_dir / f"{version}.json"
    created_at = datetime.now()

    content_path.write_text(content, encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "version": version,
                "label": label,
                "filename": filename,
                "createdAt": created_at.isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return LrcVersionRecord(
        version=version,
        label=label,
        filename=filename,
        contentPath=str(content_path.relative_to(project_store.PROJECTS_DIR)),
        metadataPath=str(metadata_path.relative_to(project_store.PROJECTS_DIR)),
        createdAt=created_at,
    )


def generate_lrc(project_id: str, lyrics_version: str | None, method: str = "draft") -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    lyrics_content = _lyrics_content_from_project(project_id, lyrics_version)
    lrc_content = _draft_lrc_from_lyrics(lyrics_content)
    version_record = _write_lrc_files(project_id, lrc_content, label=method)
    asset_record = ProjectAssetRecord(
        id=version_record.version,
        label=version_record.label,
        filename=version_record.filename,
        path=version_record.contentPath,
        metadataPath=version_record.metadataPath,
        createdAt=version_record.createdAt,
        updatedAt=version_record.createdAt,
    )
    project_service.add_project_asset(project_id, "lrcFiles", asset_record)
    updated = project_store.get_project(project_id)
    updated.selectedLrcFile = version_record.version
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return asset_record


def save_lrc(project_id: str, content: str, audio_file_id: str | None, label: str) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    version_record = _write_lrc_files(project_id, content, label=label)
    asset_record = ProjectAssetRecord(
        id=version_record.version,
        label=version_record.label,
        filename=version_record.filename,
        path=version_record.contentPath,
        metadataPath=version_record.metadataPath,
        createdAt=version_record.createdAt,
        updatedAt=version_record.createdAt,
    )
    project_service.add_project_asset(project_id, "lrcFiles", asset_record)
    updated = project_store.get_project(project_id)
    updated.selectedLrcFile = version_record.version
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return asset_record


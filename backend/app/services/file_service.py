import json
import re
from datetime import datetime
from pathlib import Path

from app.models.project import ProjectAssetRecord
import app.services.project_service as project_service
from app.storage import project_store

VOCALS_DIR_NAME = "vocals"
AUDIO_DIR_NAME = "audio"
PROMPTS_DIR_NAME = "prompts"
MUSIC_PLANS_DIR_NAME = "music_plans"
METADATA_DIR_NAME = "metadata"

ALLOWED_VOCAL_EXTENSIONS = {".wav", ".mp3", ".m4a"}


def _project_dir(project_id: str) -> Path:
    return project_store.PROJECTS_DIR / project_id


def _collection_dir(project_id: str, collection_name: str) -> Path:
    return _project_dir(project_id) / collection_name


def _metadata_dir(project_id: str) -> Path:
    return _collection_dir(project_id, METADATA_DIR_NAME)


def _safe_stem(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower()).strip("_")
    return slug or "file"


def _next_number(project_id: str, collection_name: str) -> int:
    project = project_store.get_project(project_id)
    if not project:
        return 1
    collection = getattr(project.assets, collection_name, [])
    return len(collection) + 1


def _write_asset(
    *,
    project_id: str,
    collection_name: str,
    asset_prefix: str,
    original_filename: str | None,
    extension: str,
    content: bytes,
) -> ProjectAssetRecord:
    number = _next_number(project_id, collection_name)
    safe_name = _safe_stem(asset_prefix)
    filename = f"{safe_name}_{number:03d}{extension}"
    created_at = datetime.now()

    collection_dir = _collection_dir(project_id, collection_name)
    metadata_dir = _metadata_dir(project_id)
    collection_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    file_path = collection_dir / filename
    metadata_path = metadata_dir / f"{safe_name}_{number:03d}.json"
    file_path.write_bytes(content)
    metadata_path.write_text(
        json.dumps(
            {
                "assetPrefix": safe_name,
                "filename": filename,
                "originalFilename": original_filename,
                "createdAt": created_at.isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return ProjectAssetRecord(
        id=f"{safe_name}_{number:03d}",
        label=safe_name,
        filename=filename,
        originalFilename=original_filename,
        path=str(file_path.relative_to(project_store.PROJECTS_DIR)),
        metadataPath=str(metadata_path.relative_to(project_store.PROJECTS_DIR)),
        createdAt=created_at,
        updatedAt=created_at,
    )


def upload_vocal(project_id: str, filename: str, content: bytes) -> ProjectAssetRecord:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_VOCAL_EXTENSIONS:
        raise ValueError("Unsupported vocal file type. Use wav, mp3, or m4a.")

    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    record = _write_asset(
        project_id=project_id,
        collection_name="vocalFiles",
        asset_prefix="vocal_take",
        original_filename=filename,
        extension=extension,
        content=content,
    )
    project_service.add_project_asset(project_id, "vocalFiles", record)
    return record


def add_audio_asset(
    project_id: str,
    asset_prefix: str,
    content: bytes,
    original_filename: str | None = None,
) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    record = _write_asset(
        project_id=project_id,
        collection_name="audioFiles",
        asset_prefix=asset_prefix,
        original_filename=original_filename,
        extension=".wav",
        content=content,
    )
    project_service.add_project_asset(project_id, "audioFiles", record)
    updated = project_store.get_project(project_id)
    updated.selectedAudioFile = record.id
    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return record


def add_audio_asset_from_path(project_id: str, path: Path, asset_prefix: str = "generated") -> ProjectAssetRecord:
    return add_audio_asset(
        project_id=project_id,
        asset_prefix=asset_prefix,
        content=path.read_bytes(),
        original_filename=path.name,
    )


def add_prompt_asset(project_id: str, prompt_name: str, content: str) -> ProjectAssetRecord:
    return add_text_asset(
        project_id=project_id,
        collection_name=PROMPTS_DIR_NAME,
        asset_collection_name="promptFiles",
        asset_prefix=prompt_name,
        content=content,
    )


def add_json_asset(
    *,
    project_id: str,
    collection_name: str,
    asset_collection_name: str,
    asset_prefix: str,
    content: dict,
) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    number = _next_number(project_id, asset_collection_name)
    safe_name = _safe_stem(asset_prefix)
    filename = f"{safe_name}_{number:03d}.json"
    created_at = datetime.now()

    json_dir = _collection_dir(project_id, collection_name)
    metadata_dir = _metadata_dir(project_id)
    json_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    file_path = json_dir / filename
    metadata_path = metadata_dir / f"{safe_name}_{number:03d}.json"
    file_path.write_text(
        json.dumps(content, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(
            {
                "filename": filename,
                "createdAt": created_at.isoformat(),
                "assetPrefix": safe_name,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    record = ProjectAssetRecord(
        id=f"{safe_name}_{number:03d}",
        label=safe_name,
        filename=filename,
        path=str(file_path.relative_to(project_store.PROJECTS_DIR)),
        metadataPath=str(metadata_path.relative_to(project_store.PROJECTS_DIR)),
        createdAt=created_at,
        updatedAt=created_at,
    )
    project_service.add_project_asset(project_id, asset_collection_name, record)
    return record


def add_text_asset(
    *,
    project_id: str,
    collection_name: str,
    asset_collection_name: str,
    asset_prefix: str,
    content: str,
) -> ProjectAssetRecord:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    number = _next_number(project_id, asset_collection_name)
    safe_name = _safe_stem(asset_prefix)
    filename = f"{safe_name}_{number:03d}.txt"
    created_at = datetime.now()

    text_dir = _collection_dir(project_id, collection_name)
    metadata_dir = _metadata_dir(project_id)
    text_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    file_path = text_dir / filename
    metadata_path = metadata_dir / f"{safe_name}_{number:03d}.json"
    file_path.write_text(content, encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "filename": filename,
                "createdAt": created_at.isoformat(),
                "assetPrefix": safe_name,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    record = ProjectAssetRecord(
        id=f"{safe_name}_{number:03d}",
        label=safe_name,
        filename=filename,
        path=str(file_path.relative_to(project_store.PROJECTS_DIR)),
        metadataPath=str(metadata_path.relative_to(project_store.PROJECTS_DIR)),
        createdAt=created_at,
        updatedAt=created_at,
    )
    project_service.add_project_asset(project_id, asset_collection_name, record)
    return record


def list_audio_assets(project_id: str) -> list[ProjectAssetRecord]:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    return project.assets.audioFiles


def get_audio_asset(project_id: str, audio_id: str) -> ProjectAssetRecord | None:
    project = project_store.get_project(project_id)
    if not project:
        return None
    for record in project.assets.audioFiles:
        if record.id == audio_id:
            return record
    return None


def get_asset_file_path(record: ProjectAssetRecord) -> Path:
    if not record.path:
        raise ValueError(f"Asset {record.id} does not have a file path")
    return project_store.PROJECTS_DIR / record.path

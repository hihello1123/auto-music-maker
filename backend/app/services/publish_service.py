import json
from datetime import datetime
from pathlib import Path

from app.models.publish import PublishInfoResponse
from app.storage import project_store

METADATA_DIR_NAME = "metadata"


def _project_dir(project_id: str) -> Path:
    return project_store.PROJECTS_DIR / project_id


def _metadata_dir(project_id: str) -> Path:
    return _project_dir(project_id) / METADATA_DIR_NAME


def _read_text_file(relative_path: str | None) -> str:
    if not relative_path:
        return ""
    file_path = project_store.PROJECTS_DIR / relative_path
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def generate_publish_info(project_id: str, title_hint: str | None = None) -> PublishInfoResponse:
    project = project_store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    lyrics_content = ""
    if project.selectedLyricsVersion:
        for record in project.assets.lyricsVersions:
            if record.id == project.selectedLyricsVersion:
                lyrics_content = _read_text_file(record.path)
                break

    audio_label = project.selectedAudioFile or "final take"
    base_title = title_hint or project.title or "Untitled Song"
    title_candidates = [
        base_title,
        f"{base_title} | {project.theme}" if project.theme else base_title,
        f"{base_title} ({audio_label})",
    ]

    description_lines = [
        f"Title: {base_title}",
    ]
    if project.theme:
        description_lines.append(f"Theme: {project.theme}")
    if project.genre:
        description_lines.append(f"Genre: {project.genre}")
    if lyrics_content:
        description_lines.append("")
        description_lines.append("Lyrics:")
        description_lines.append(lyrics_content[:1000])

    ai_disclosure = (
        "이 곡은 제가 직접 작성한 가사와 직접 녹음한 보컬을 기반으로 제작되었습니다.\n"
        "일부 배경음악/편곡 요소는 AI 음악 생성 도구를 활용했으며,\n"
        "최종 구성, 보컬 녹음, 편집 및 선별은 직접 진행했습니다."
    )

    checklist = [
        "제목과 설명란 최종 확인",
        "썸네일 확인",
        "공개 범위 선택",
        "AI 사용 고지 포함 확인",
        "오디오와 LRC 싱크 확인",
    ]

    response = PublishInfoResponse(
        titleCandidates=title_candidates,
        description="\n".join(description_lines),
        tags=[tag for tag in {project.genre or "", project.language, "ai music", "short form"} if tag],
        aiDisclosure=ai_disclosure,
        checklist=checklist,
        generatedAt=datetime.now(),
    )

    metadata_dir = _metadata_dir(project_id)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    output_path = metadata_dir / "publish_info.json"
    output_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")
    return response


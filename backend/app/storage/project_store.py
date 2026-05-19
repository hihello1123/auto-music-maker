import json
from pathlib import Path
from typing import Optional

from app.models.project import Project

# 프로젝트 데이터 디렉토리 (backend/data/projects/)
PROJECTS_DIR = Path(__file__).resolve().parents[2] / "data" / "projects"


def _ensure_dir() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _project_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id


def _project_file(project_id: str) -> Path:
    return _project_dir(project_id) / "project.json"


def save_project(project: Project) -> None:
    """프로젝트를 JSON 파일로 저장"""
    _ensure_dir()
    dir_path = _project_dir(project.id)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = _project_file(project.id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(project.model_dump(), f, ensure_ascii=False, indent=2, default=str)


def get_project(project_id: str) -> Optional[Project]:
    """프로젝트 JSON 파일을 읽어서 Project 객체로 반환"""
    file_path = _project_file(project_id)
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Project(**data)


def list_projects() -> list[Project]:
    """모든 프로젝트 목록 반환"""
    _ensure_dir()
    projects: list[Project] = []
    for entry in PROJECTS_DIR.iterdir():
        if entry.is_dir():
            file_path = entry / "project.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                projects.append(Project(**data))
    return projects


def delete_project(project_id: str) -> bool:
    """프로젝트 디렉토리 전체 삭제"""
    import shutil
    dir_path = _project_dir(project_id)
    if dir_path.exists():
        shutil.rmtree(dir_path)
        return True
    return False

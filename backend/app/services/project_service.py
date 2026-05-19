import uuid
from datetime import datetime

from app.models.project import Project, ProjectAssetRecord, ProjectCreate, ProjectUpdate
from app.storage import project_store


def create_project(data: ProjectCreate) -> Project:
    """새 프로젝트 생성"""
    project_id = str(uuid.uuid4())
    now = datetime.now()
    project = Project(
        id=project_id,
        title=data.title,
        theme=data.theme,
        language=data.language,
        createdAt=now,
        updatedAt=now,
    )
    project_store.save_project(project)
    return project


def get_project(project_id: str) -> Project | None:
    """프로젝트 조회"""
    return project_store.get_project(project_id)


def get_projects() -> list[Project]:
    """프로젝트 목록 조회"""
    return project_store.list_projects()


def update_project(project_id: str, data: ProjectUpdate) -> Project | None:
    """프로젝트 수정"""
    existing = project_store.get_project(project_id)
    if not existing:
        return None

    updated = existing.model_copy()
    update_dict = data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(updated, key, value)

    updated.updatedAt = datetime.now()
    project_store.save_project(updated)
    return updated


def delete_project(project_id: str) -> bool:
    """프로젝트 삭제"""
    return project_store.delete_project(project_id)


def register_job(project_id: str, job_id: str) -> Project | None:
    """프로젝트에 job id를 기록"""
    existing = project_store.get_project(project_id)
    if not existing:
        return None

    if job_id not in existing.assets.jobIds:
        existing.assets.jobIds.append(job_id)
        existing.updatedAt = datetime.now()
        project_store.save_project(existing)

    return existing


def add_project_asset(project_id: str, collection_name: str, record: ProjectAssetRecord) -> Project | None:
    """프로젝트 자산 레코드 추가"""
    existing = project_store.get_project(project_id)
    if not existing:
        return None

    collection = getattr(existing.assets, collection_name, None)
    if collection is None:
        return None

    collection.append(record)
    existing.updatedAt = datetime.now()
    project_store.save_project(existing)
    return existing

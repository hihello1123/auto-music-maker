from fastapi import APIRouter, HTTPException

from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[Project])
def list_projects():
    """프로젝트 목록 조회"""
    return project_service.get_projects()


@router.post("", response_model=Project, status_code=201)
def create_project(data: ProjectCreate):
    """새 프로젝트 생성"""
    return project_service.create_project(data)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str):
    """프로젝트 상세 조회"""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


@router.patch("/{project_id}", response_model=Project)
def update_project(project_id: str, data: ProjectUpdate):
    """프로젝트 수정"""
    project = project_service.update_project(project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str):
    """프로젝트 삭제"""
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

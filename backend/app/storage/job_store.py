import json
from pathlib import Path
from typing import Optional

from app.models.job import Job

# backend/data/projects/{project_id}/jobs/
PROJECTS_DIR = Path(__file__).resolve().parents[2] / "data" / "projects"


def _project_jobs_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id / "jobs"


def _job_file(project_id: str, job_id: str) -> Path:
    return _project_jobs_dir(project_id) / f"{job_id}.json"


def save_job(job: Job) -> None:
    """job를 프로젝트 하위 jobs 폴더에 저장"""
    dir_path = _project_jobs_dir(job.projectId)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = _job_file(job.projectId, job.id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(job.model_dump(), f, ensure_ascii=False, indent=2, default=str)


def get_job(job_id: str) -> Optional[Job]:
    """프로젝트들을 순회하며 job을 찾음"""
    if not PROJECTS_DIR.exists():
        return None

    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        jobs_dir = project_dir / "jobs"
        if not jobs_dir.exists():
            continue
        file_path = jobs_dir / f"{job_id}.json"
        if not file_path.exists():
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Job(**data)
    return None


def list_jobs(project_id: str | None = None) -> list[Job]:
    """전체 job 또는 프로젝트별 job 목록 반환"""
    jobs: list[Job] = []
    if not PROJECTS_DIR.exists():
        return jobs

    if project_id:
        jobs_dir = _project_jobs_dir(project_id)
        if not jobs_dir.exists():
            return jobs
        for entry in jobs_dir.glob("*.json"):
            with open(entry, "r", encoding="utf-8") as f:
                jobs.append(Job(**json.load(f)))
        return jobs

    for project_dir in PROJECTS_DIR.iterdir():
        jobs_dir = project_dir / "jobs"
        if not jobs_dir.exists():
            continue
        for entry in jobs_dir.glob("*.json"):
            with open(entry, "r", encoding="utf-8") as f:
                jobs.append(Job(**json.load(f)))
    return jobs


import uuid
from datetime import datetime

from app.models.job import Job, JobCreate, JobLogEntry, JobStatus, JobUpdate
from app.services.project_service import register_job
from app.storage import job_store


def create_job(data: JobCreate) -> Job:
    """새 job 생성"""
    job = Job(
        id=str(uuid.uuid4()),
        type=data.type,
        projectId=data.projectId,
        status=JobStatus.queued,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    job_store.save_job(job)
    register_job(data.projectId, job.id)
    return job


def get_job(job_id: str) -> Job | None:
    """job 조회"""
    return job_store.get_job(job_id)


def list_jobs(project_id: str | None = None) -> list[Job]:
    """job 목록 조회"""
    return job_store.list_jobs(project_id)


def update_job(job_id: str, data: JobUpdate) -> Job | None:
    """job 상태/결과 갱신"""
    existing = job_store.get_job(job_id)
    if not existing:
        return None

    updated = existing.model_copy()
    payload = data.model_dump(exclude_unset=True)

    message = payload.pop("message", None)
    for key, value in payload.items():
        setattr(updated, key, value)

    if message:
        updated.log.append(JobLogEntry(message=message))

    updated.updatedAt = datetime.now()
    job_store.save_job(updated)
    return updated

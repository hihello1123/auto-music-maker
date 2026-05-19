from fastapi import APIRouter, HTTPException

from app.models.job import Job
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: str):
    """job 상세 조회"""
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


from fastapi import APIRouter, HTTPException

from app.models.music import MusicGenerateRequest, MusicGenerateResponse, MusicPlanResponse
from app.services import music_plan_service, music_service

router = APIRouter(prefix="/projects/{project_id}/music", tags=["music"])


@router.post("/spec/generate", response_model=MusicPlanResponse, status_code=202)
def generate_music_spec(project_id: str, data: MusicGenerateRequest):
    """ACE-Step LM 기반 곡 스펙 생성"""
    try:
        return music_plan_service.generate_music_plan(project_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/generate", response_model=MusicGenerateResponse, status_code=202)
def generate_music(project_id: str, data: MusicGenerateRequest):
    """음악 생성 요청 스켈레톤"""
    try:
        return music_service.generate_music(project_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

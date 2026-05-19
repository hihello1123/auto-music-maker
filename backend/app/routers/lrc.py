from fastapi import APIRouter, HTTPException

from app.models.lrc import LrcGenerateRequest, LrcSaveRequest
from app.models.project import ProjectAssetRecord
from app.services import lrc_service

router = APIRouter(prefix="/projects/{project_id}/lrc", tags=["lrc"])


@router.post("/generate", response_model=ProjectAssetRecord, status_code=201)
def generate_lrc(project_id: str, data: LrcGenerateRequest):
    """LRC 초안 생성"""
    try:
        return lrc_service.generate_lrc(project_id, data.lyricsVersion, data.method)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/save", response_model=ProjectAssetRecord, status_code=201)
def save_lrc(project_id: str, data: LrcSaveRequest):
    """LRC 수동 저장"""
    try:
        return lrc_service.save_lrc(project_id, data.content, data.audioFileId, data.label)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


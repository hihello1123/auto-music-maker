from fastapi import APIRouter, HTTPException

from app.models.lyrics import LyricsGenerateRequest, LyricsSaveRequest
from app.models.project import ProjectAssetRecord
from app.services import lyric_service

router = APIRouter(prefix="/projects/{project_id}/lyrics", tags=["lyrics"])


@router.post("/generate", response_model=ProjectAssetRecord, status_code=201)
def generate_lyrics(project_id: str, data: LyricsGenerateRequest):
    """Ollama 기반 가사 후보 생성"""
    try:
        return lyric_service.generate_lyrics(project_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/save", response_model=ProjectAssetRecord, status_code=201)
def save_lyrics(project_id: str, data: LyricsSaveRequest):
    """수동 편집된 가사 저장"""
    try:
        return lyric_service.save_lyrics(project_id, data.content, data.label)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.project import ProjectAssetRecord
from app.services import file_service

router = APIRouter(prefix="/projects/{project_id}", tags=["files"])


@router.post("/files/upload-vocal", response_model=ProjectAssetRecord, status_code=201)
async def upload_vocal(project_id: str, file: UploadFile = File(...)):
    """보컬 파일 업로드"""
    try:
        content = await file.read()
        return file_service.upload_vocal(project_id, file.filename or "vocal.wav", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/audio", response_model=list[ProjectAssetRecord])
def list_audio(project_id: str):
    """오디오 파일 목록"""
    try:
        return file_service.list_audio_assets(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/audio/{audio_id}")
def get_audio(project_id: str, audio_id: str):
    """오디오 파일 스트리밍/다운로드"""
    record = file_service.get_audio_asset(project_id, audio_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audio {audio_id} not found")

    file_path = file_service.get_asset_file_path(record)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Audio file {record.path} not found")
    return FileResponse(path=file_path, filename=record.filename or file_path.name)


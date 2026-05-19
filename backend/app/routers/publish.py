from fastapi import APIRouter, HTTPException

from app.models.publish import PublishInfoGenerateRequest, PublishInfoResponse
from app.services import publish_service

router = APIRouter(prefix="/projects/{project_id}/publish-info", tags=["publish"])


@router.post("/generate", response_model=PublishInfoResponse)
def generate_publish_info(project_id: str, data: PublishInfoGenerateRequest):
    """유튜브 수동 업로드용 메타데이터 생성"""
    try:
        return publish_service.generate_publish_info(project_id, data.titleHint)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


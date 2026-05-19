from datetime import datetime

from pydantic import BaseModel, Field


class PublishInfoGenerateRequest(BaseModel):
    audioFileId: str | None = None
    lyricsVersion: str | None = None
    titleHint: str | None = None


class PublishInfoResponse(BaseModel):
    titleCandidates: list[str]
    description: str
    tags: list[str]
    aiDisclosure: str
    checklist: list[str]
    generatedAt: datetime = Field(default_factory=datetime.now)


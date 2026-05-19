from datetime import datetime

from pydantic import BaseModel, Field


class LrcGenerateRequest(BaseModel):
    audioFileId: str | None = None
    lyricsVersion: str | None = None
    method: str = "draft"


class LrcSaveRequest(BaseModel):
    content: str
    audioFileId: str | None = None
    label: str = "manual_edit"


class LrcVersionRecord(BaseModel):
    version: str
    label: str
    filename: str
    contentPath: str
    metadataPath: str
    createdAt: datetime = Field(default_factory=datetime.now)


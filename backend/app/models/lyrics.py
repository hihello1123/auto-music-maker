from datetime import datetime

from pydantic import BaseModel, Field


class LyricsGenerateRequest(BaseModel):
    model: str | None = None
    theme: str | None = None
    language: str = "en"
    style: str | None = None
    instruction: str | None = None
    versionCount: int = 1


class LyricsSaveRequest(BaseModel):
    content: str
    label: str = "manual_edit"


class LyricsVersionRecord(BaseModel):
    version: str
    label: str
    filename: str
    contentPath: str
    metadataPath: str
    createdAt: datetime = Field(default_factory=datetime.now)


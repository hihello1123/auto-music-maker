from datetime import datetime

from pydantic import BaseModel, Field


class MusicPlanResponse(BaseModel):
    musicPlanFileId: str | None = None
    promptPresetId: str | None = None
    promptPresetLabel: str | None = None
    sourcePrompt: str
    caption: str
    lyrics: str
    genre: str | None = None
    bpm: int | None = None
    key: str | None = None
    duration: int | None = None
    timeSignature: str | None = None
    language: str | None = None
    engine: str = "ace-step-lm"
    createdAt: datetime = Field(default_factory=datetime.now)


class MusicGenerateRequest(BaseModel):
    mode: str = "lyrics_only"
    lyricsVersion: str | None = None
    promptPresetId: str | None = None
    songStructure: str = "chorus_only"
    genre: str | None = None
    bpm: int | None = None
    key: str | None = None
    duration: int = 60
    seed: int | None = None
    count: int = 1
    instrumentalOnly: bool = False
    noAdditionalVocals: bool = False
    preserveMelody: bool = False
    vocalFileId: str | None = None


class MusicGenerateResponse(BaseModel):
    jobId: str
    prompt: str
    mode: str
    seed: int | None = None
    promptFileId: str | None = None
    musicPlanFileId: str | None = None
    promptPresetId: str | None = None
    audioFileIds: list[str] = Field(default_factory=list)
    engine: str = "placeholder"
    createdAt: datetime = Field(default_factory=datetime.now)

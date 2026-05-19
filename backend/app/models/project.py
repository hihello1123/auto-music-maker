from datetime import datetime

from pydantic import BaseModel, Field


class ProjectAssetRecord(BaseModel):
    id: str
    label: str | None = None
    filename: str | None = None
    originalFilename: str | None = None
    path: str | None = None
    metadataPath: str | None = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


class ProjectAssets(BaseModel):
    lyricsVersions: list[ProjectAssetRecord] = Field(default_factory=list)
    promptFiles: list[ProjectAssetRecord] = Field(default_factory=list)
    musicPlans: list[ProjectAssetRecord] = Field(default_factory=list)
    vocalFiles: list[ProjectAssetRecord] = Field(default_factory=list)
    audioFiles: list[ProjectAssetRecord] = Field(default_factory=list)
    lrcFiles: list[ProjectAssetRecord] = Field(default_factory=list)
    videoFiles: list[ProjectAssetRecord] = Field(default_factory=list)
    jobIds: list[str] = Field(default_factory=list)


class ProjectAssetCollection(str):
    LYRICS = "lyricsVersions"
    PROMPTS = "promptFiles"
    MUSIC_PLANS = "musicPlans"
    VOCALS = "vocalFiles"
    AUDIO = "audioFiles"
    LRC = "lrcFiles"
    VIDEO = "videoFiles"


class Project(BaseModel):
    id: str
    title: str
    theme: str | None = None
    language: str = "en"
    genre: str | None = None
    bpm: int | None = None
    key: str | None = None
    selectedLyricsVersion: str | None = None
    selectedPromptPreset: str | None = None
    selectedMusicPlan: str | None = None
    selectedAudioFile: str | None = None
    selectedLrcFile: str | None = None
    assets: ProjectAssets = Field(default_factory=ProjectAssets)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


class ProjectCreate(BaseModel):
    title: str
    theme: str | None = None
    language: str = "en"


class ProjectUpdate(BaseModel):
    title: str | None = None
    theme: str | None = None
    language: str | None = None
    genre: str | None = None
    bpm: int | None = None
    key: str | None = None
    selectedLyricsVersion: str | None = None
    selectedPromptPreset: str | None = None
    selectedMusicPlan: str | None = None
    selectedAudioFile: str | None = None
    selectedLrcFile: str | None = None

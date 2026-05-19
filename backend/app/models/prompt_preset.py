from datetime import datetime

from pydantic import BaseModel, Field


class PromptPreset(BaseModel):
    id: str
    label: str
    matchGenres: list[str] = Field(default_factory=list)
    blueprintGuidance: list[str] = Field(default_factory=list)
    generationGuidance: list[str] = Field(default_factory=list)
    avoidGuidance: list[str] = Field(default_factory=list)
    defaultBpm: int | None = None
    defaultKey: str | None = None
    defaultDuration: int | None = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobLogEntry(BaseModel):
    message: str
    createdAt: datetime = Field(default_factory=datetime.now)


class Job(BaseModel):
    id: str
    type: str
    status: JobStatus = JobStatus.queued
    projectId: str
    progress: float | None = None
    log: list[JobLogEntry] = Field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


class JobCreate(BaseModel):
    type: str
    projectId: str


class JobUpdate(BaseModel):
    status: JobStatus | None = None
    progress: float | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    message: str | None = None

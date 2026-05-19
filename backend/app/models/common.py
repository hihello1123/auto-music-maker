from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """공통 응답 모델"""
    data: T
    message: str = "success"


class ErrorResponse(BaseModel):
    """공통 에러 응답 모델"""
    error: str
    detail: str | None = None


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str

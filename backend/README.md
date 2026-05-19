# Backend API

로컬 AI Song Studio의 FastAPI 백엔드입니다.

## 역할

- 프로젝트 메타데이터 관리
- 가사 생성과 저장
- 프롬프트 프리셋 조회
- 곡 스펙 생성
- 음악 생성 요청
- 오디오 / LRC / publish 정보 관리
- job 상태 관리

## 요구 사항

- Python 3.11
- [uv](https://github.com/astral-sh/uv)

## 설치

```bash
cd backend
uv python install 3.11
uv sync
```

## 환경 변수

```bash
cp .env.example .env
```

필수 또는 주요 값:

- `HOST=127.0.0.1`
- `PORT=12000`
- `RELOAD=true`
- `CORS_ORIGINS=["http://localhost:3000"]`
- `OLLAMA_URL=http://localhost:11434`
- `OLLAMA_MODEL=mistral-small3.2:24b`
- `OLLAMA_TIMEOUT=0`
- `ACE_STEP_API_URL=http://127.0.0.1:12001`

ACE-Step 관련 선택값:

- `ACE_STEP_API_KEY`
- `ACE_STEP_API_MODEL`
- `ACE_STEP_API_POLL_INTERVAL`

CLI fallback:

- `ACE_STEP_CMD_TEMPLATE`
- `ACE_STEP_TIMEOUT`

## 실행

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 12000 --reload
```

## 주요 엔드포인트

- `GET /health`
- `GET /projects`
- `POST /projects`
- `GET /projects/{id}`
- `PATCH /projects/{id}`
- `DELETE /projects/{id}`
- `GET /prompt-presets`
- `GET /prompt-presets/{preset_id}`
- `GET /jobs/{id}`
- `POST /projects/{id}/lyrics/generate`
- `POST /projects/{id}/lyrics/save`
- `POST /projects/{id}/files/upload-vocal`
- `GET /projects/{id}/audio`
- `GET /projects/{id}/audio/{audio_id}`
- `POST /projects/{id}/music/spec/generate`
- `POST /projects/{id}/music/generate`
- `POST /projects/{id}/lrc/generate`
- `POST /projects/{id}/lrc/save`
- `POST /projects/{id}/publish-info/generate`

## 저장 위치

- `backend/data/projects/{project_id}/`
- `lyrics/`
- `prompts/`
- `music_plans/`
- `vocals/`
- `audio/`
- `lrc/`
- `video/`
- `metadata/`


# Backend API

FastAPI 기반 로컬 AI Song Studio 백엔드입니다. 작업 목표와 티켓은 [`docs/planning/backend/`](../docs/planning/backend/)를 기준으로 봅니다.

## 요구 사항

- Python 3.11
- [uv](https://github.com/astral-sh/uv) 패키지 매니저

## 설치

```bash
cd backend
uv python install 3.11
uv sync
```

## 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 서버 설정을 변경할 수 있습니다.

ACE-Step를 실제 API 서버로 연결하려면 `ACE_STEP_API_URL=http://127.0.0.1:8001` 를 넣습니다.
로컬 단독 사용이면 `ACE_STEP_API_KEY` 는 비워도 됩니다.
곡 스펙까지 ACE-Step LM으로 정리하려면 ACE-Step API 서버를 `ACESTEP_INIT_LLM=true` 와 LM 모델 경로로 실행해야 합니다.

## 환경 변수 요약

- 필수: `HOST`, `PORT`, `RELOAD`, `CORS_ORIGINS`
- 가사 생성: `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT` (`0` 또는 비워두면 무제한)
- ACE-Step 로컬 API: `ACE_STEP_API_URL`
- ACE-Step 선택 항목: `ACE_STEP_API_KEY`, `ACE_STEP_API_MODEL`, `ACE_STEP_API_POLL_INTERVAL`
- CLI fallback: `ACE_STEP_CMD_TEMPLATE`, `ACE_STEP_TIMEOUT`

## 실행

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 12000 --reload
```

또는 Python 스크립트로 직접 실행:

```bash
uv run python -m app.main
```

## 엔드포인트

| 메서드 | 경로             | 설명             |
|--------|------------------|------------------|
| GET    | `/health`        | 헬스 체크        |
| GET    | `/projects`      | 프로젝트 목록    |
| POST   | `/projects`      | 프로젝트 생성    |
| GET    | `/projects/{id}` | 프로젝트 상세    |
| PATCH  | `/projects/{id}` | 프로젝트 수정    |
| DELETE | `/projects/{id}` | 프로젝트 삭제    |
| GET    | `/prompt-presets` | 프롬프트 프리셋 목록 |
| GET    | `/prompt-presets/{preset_id}` | 프롬프트 프리셋 상세 |
| GET    | `/jobs/{id}`     | job 상세 조회    |
| POST   | `/projects/{id}/lyrics/generate` | 가사 생성 |
| POST   | `/projects/{id}/lyrics/save` | 가사 저장 |
| POST   | `/projects/{id}/files/upload-vocal` | 보컬 업로드 |
| GET    | `/projects/{id}/audio` | 오디오 목록 |
| GET    | `/projects/{id}/audio/{audio_id}` | 오디오 다운로드 |
| POST   | `/projects/{id}/music/spec/generate` | 곡 스펙 생성 |
| POST   | `/projects/{id}/music/generate` | 음악 생성 요청 |
| POST   | `/projects/{id}/lrc/generate` | LRC 생성 |
| POST   | `/projects/{id}/lrc/save` | LRC 저장 |
| POST   | `/projects/{id}/publish-info/generate` | publish 정보 생성 |

현재 구현된 기본 자원은 프로젝트 API입니다. 나머지 기능은 기획 문서의 티켓 순서에 맞춰 순차적으로 확장합니다.

## 프로젝트 구조

```
backend/
├── pyproject.toml
├── .env.example
├── README.md
└── app/
    ├── __init__.py
    ├── main.py
    └── config.py
```

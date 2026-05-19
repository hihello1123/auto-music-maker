# Local AI Song Studio

로컬에서 혼자 쓰는 AI 음악 제작 작업실입니다.

한 화면에서 다음 흐름을 이어서 다룹니다.

- 프로젝트 생성과 선택
- 가사 버전 관리
- 곡 스펙 생성
- 음악 생성
- 오디오 / LRC / publish 정보 관리
- job 상태 확인

세부 기획 문서는 [`docs/planning/README.md`](./docs/planning/README.md)를 기준으로 봅니다.

## 구조

- `backend/`: FastAPI 기반 실행 엔진
- `frontend/`: Next.js 기반 로컬 작업 대시보드
- `docs/planning/`: 기능별 기획 문서
- `DESIGN.md`: 한 페이지 작업실 UI 기준

## 실행 순서

1. `backend/.env` 설정
2. Ollama 실행
3. ACE-Step API 실행
4. 백엔드 실행
5. 프런트 실행

## 빠른 시작

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 12000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

기본 API 주소는 `http://127.0.0.1:12000`입니다. 프런트에서 바꾸려면 `frontend/.env.local`에 아래를 넣습니다.

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:12000
```

## 전체 목표

- 한국어 감정선을 바탕으로 영어 가사 후보를 만들 수 있어야 합니다.
- 선택한 가사를 기준으로 곡 스펙을 만들고, 그 스펙으로 음악 생성 요청을 보낼 수 있어야 합니다.
- 생성된 결과물은 프로젝트 단위로 파일과 메타데이터를 함께 관리해야 합니다.
- 긴 작업은 job으로 추적하고, 프런트에서 진행 상태를 확인할 수 있어야 합니다.
- 최종적으로는 수동 업로드용 설명, 태그, 체크리스트까지 생성할 수 있어야 합니다.

## 파트별 목표

- 백엔드/프런트 목표는 `docs/planning/backend/overview.md`와 `docs/planning/frontend/overview.md`로 분리했습니다.
- 공통 원칙은 `docs/planning/shared/`에 둡니다.
- 구현 원칙은 각 기능 문서에만 남기고, 루트 README는 진입점만 제공합니다.

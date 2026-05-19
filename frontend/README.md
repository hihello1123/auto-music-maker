# Frontend Goals

프런트 기획 문서는 [`docs/planning/frontend/`](../docs/planning/frontend/)를 기준으로 본다.

현재 프런트가 맡는 역할:

- 로컬 대시보드 제공
- 프로젝트와 결과물 관리
- 가사/오디오/LRC/영상 작업 흐름 연결
- 백엔드 FastAPI API 호출

## 실행

```bash
cd frontend
npm install
npm run dev
```

기본 API 주소는 `http://127.0.0.1:12000` 이고, 변경하려면 `.env.local`에 아래 값을 넣는다.

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:12000
```

현재 프런트 화면에서 할 수 있는 것:

- 프로젝트 선택
- 프롬프트 프리셋 선택
- `chorus_only` 쇼츠 구조 선택
- 스펙 생성
- 음악 생성
- 생성 결과 JSON 확인

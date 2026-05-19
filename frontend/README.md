# Frontend

로컬 AI Song Studio의 Next.js 작업 대시보드입니다.

## 역할

- 한 화면에서 작업 흐름을 보여주기
- 프로젝트 생성과 선택
- 프롬프트 프리셋 / 가사 버전 / 구조 선택
- 곡 스펙 생성과 음악 생성 요청
- 결과 JSON 확인

## 실행

```bash
cd frontend
npm install
npm run dev
```

기본 API 주소:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:12000
```

## 현재 화면에서 할 수 있는 것

- 프로젝트 생성
- 프로젝트 선택
- 프롬프트 프리셋 선택
- `chorus_only` 쇼츠 구조 선택
- `lyrics_only` / `vocal_to_bgm` / `instrumental` / `reference_audio` 선택
- 스펙 생성
- 음악 생성
- 생성 결과 JSON 확인

## 화면 방향

- 다크모드 전용
- 로컬 작업실 느낌
- 한 페이지 중심
- 왼쪽: 프로젝트와 자산
- 가운데: 작업대
- 오른쪽: 프리셋과 결과 요약


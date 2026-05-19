# Local AI Song Studio

로컬에서 AI 기반 작곡, 가사 작성, 오디오 생성, LRC, 숏폼 영상 메타데이터까지 관리하는 프로젝트입니다.

세부 기획 문서는 [`docs/planning/README.md`](./docs/planning/README.md)를 기준으로 봅니다.

## 전체 목표

- 사용자가 한국어 감정선을 입력하면 영어 가사 후보를 만들 수 있어야 합니다.
- 선택한 가사를 기준으로 로컬 AI 음악 생성 요청을 만들 수 있어야 합니다.
- 생성된 결과물은 프로젝트 단위로 파일과 메타데이터를 함께 관리해야 합니다.
- 긴 작업은 모두 job으로 처리하고, 프런트에서는 진행 상태를 확인할 수 있어야 합니다.
- 최종적으로는 수동 업로드용 설명, 태그, 체크리스트까지 생성할 수 있어야 합니다.

## 파트별 목표

- 백엔드/프런트 목표는 `docs/planning/backend/overview.md`와 `docs/planning/frontend/overview.md`로 분리했습니다.
- 공통 원칙은 `docs/planning/shared/`에 둡니다.
- 구현 원칙은 각 기능 문서에만 남기고, 루트 README는 진입점만 제공합니다.

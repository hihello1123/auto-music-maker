# Ticket 05 - Music Request Skeleton

## Goal

ACE-Step에 넘길 음악 생성 요청을 백엔드가 책임지고 정리한다.

## Scope

- mode 모델
- prompt generation
- request validation
- result metadata skeleton

## Output

- `lyrics_only`, `vocal_to_bgm`, `instrumental`, `reference_audio` 구분
- 실제 실행 전의 요청 기록 구조

## Success Criteria

- 프런트 계약이 ACE-Step 실행 방식과 분리된다.
- 나중에 REST, CLI, Python API로 바뀌어도 API는 유지된다.


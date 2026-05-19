# Ticket 07 - Ollama and Integrations

## Goal

백엔드의 외부 연동 계층을 서비스로 분리한다.

## Scope

- Ollama service
- ACE-Step service stub
- ffmpeg helper boundary
- future LRC service boundary

## Output

- 연동별 service 경계
- 호출 방식 교체가 쉬운 구조

## Success Criteria

- 외부 도구가 바뀌어도 API 계층이 흔들리지 않는다.
- 기능별 코드가 service 계층에 정리된다.


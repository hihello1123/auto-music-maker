# Ticket 02 - Job Tracking

## Goal

오래 걸리는 작업을 job으로 관리한다.

## Scope

- job 모델
- job store
- job status enum
- job detail endpoint

## Output

- `queued`, `running`, `completed`, `failed` 상태 정의
- job 로그와 error 저장 구조

## Success Criteria

- 프런트가 `GET /jobs/{job_id}`로 진행 상태를 확인할 수 있다.
- job 실패 시 원인을 남긴다.


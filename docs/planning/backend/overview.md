# Backend Overview

로컬 AI Song Studio 백엔드의 목표와 MVP 범위를 정리한다.

## 역할

- 프로젝트를 저장하고 조회한다.
- 가사 생성과 저장을 관리한다.
- 보컬 파일과 오디오 파일을 프로젝트 단위로 관리한다.
- job 상태를 추적한다.
- 나중에 ACE-Step, LRC, video 렌더링을 붙일 수 있는 구조를 만든다.

## MVP 범위

1. 프로젝트 CRUD
2. Ollama 기반 가사 후보 생성
3. 가사 버전 저장
4. 보컬 파일 업로드
5. ACE-Step용 prompt 생성
6. 음악 생성 job 등록
7. 오디오 목록 조회
8. 오디오 스트리밍/다운로드
9. job 상태 조회

## 2차 목표

- ACE-Step 실제 연동
- LRC 자동 생성
- 숏폼 영상 렌더링
- publish 정보 생성


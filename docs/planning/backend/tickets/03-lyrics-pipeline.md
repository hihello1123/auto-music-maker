# Ticket 03 - Lyrics Pipeline

## Goal

Ollama로 영어 가사 후보를 생성하고, 버전으로 저장한다.

## Scope

- Ollama service
- lyrics generate endpoint
- lyrics save endpoint
- versioned markdown storage

## Output

- 가사 후보 저장 구조
- 선택된 가사 버전 기록

## Success Criteria

- 사용자가 생성 결과를 보고 수정할 수 있다.
- 덮어쓰기 대신 새 버전이 쌓인다.


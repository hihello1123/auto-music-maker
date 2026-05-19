# Lyrics Compare Flow

Ollama와 ACE-Step의 "가사 생성" 성향을 비교하기 위한 로컬 비교 플로우다.

## 비교 범위

- Ollama: 가사 초안 생성
- ACE-Step: `create_sample` 또는 `format_sample` 기반의 LM 출력

## 중요한 전제

- Ollama는 이미 별도 가사 생성 엔진으로 쓰고 있다.
- ACE-Step는 음악 생성 엔진이지만 내부 LM이 있어 가사/캡션 보조가 가능하다.
- ACE-Step의 LM 비교를 하려면 `ACESTEP_INIT_LLM=true`가 필요하다.
- `ACESTEP_INIT_LLM=false` 상태에서는 음악 생성만 가능하고, 가사 비교는 할 수 없다.

## 비교 입력

같은 입력을 두 엔진에 넣는다.

- theme
- language
- style
- instruction
- versionCount

예시:

```text
theme: 밤이 조용할수록 잊은 줄 알았던 목소리가 더 선명해진다
language: en
style: emotional pop ballad
instruction: easy English, short lines, singable
versionCount: 3
```

## 비교 항목

- 자연스러움
- 감정선 일관성
- 훅/후렴 인상
- 싱어블함
- 지시사항 준수
- 출력 속도

## 추천 실행 순서

1. Ollama로 가사 초안 생성
2. ACE-Step LM으로 같은 입력을 처리
3. 두 결과를 저장
4. 위 항목으로 수동 점수화
5. 마음에 드는 결과를 프로젝트의 `lyrics_vN.md`로 저장

## Ollama 실행

```bash
curl -sS -X POST http://127.0.0.1:12000/projects/{project_id}/lyrics/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "mistral-small3.2:24b",
    "theme": "...",
    "language": "en",
    "style": "emotional pop ballad",
    "instruction": "easy English, short lines, singable",
    "versionCount": 3
  }'
```

## ACE-Step 비교 실행

ACE-Step의 API 서버만으로는 LM 비교가 애매하므로, 아래 둘 중 하나를 쓴다.

### 방법 A: `profile_inference.py`

```bash
cd /Users/george/auto-music/external/ACE-Step-1.5
ACESTEP_INIT_LLM=true \
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-0.6B \
uv run python profile_inference.py --mode create_sample --sample-query "a soft emotional pop ballad about rain and memory"
```

### 방법 B: `format_input`

이미 가사 초안이 있을 때, 그걸 ACE-Step LM으로 다듬는 용도.

```bash
cd /Users/george/auto-music/external/ACE-Step-1.5
ACESTEP_INIT_LLM=true \
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-0.6B \
uv run acestep-api --host 127.0.0.1 --port 12001
```

그 다음:

```bash
curl -sS -X POST http://127.0.0.1:12001/format_input \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "emotional pop ballad",
    "lyrics": "I still hear your name in the rain"
  }'
```

## 해석 기준

- Ollama는 "처음부터 가사를 만드는 능력"에 더 가깝다.
- ACE-Step는 "음악 제작 문맥에 맞게 캡션/가사/메타를 정리하는 능력"에 더 가깝다.
- 그래서 완전한 1:1 비교보다는, 같은 입력에 대한 **가사 초안 품질 vs 음악 문맥 보조 품질** 비교로 보는 게 맞다.


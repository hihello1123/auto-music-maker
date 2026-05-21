import json
import re
from urllib import error, request

from app.config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL


class OllamaServiceError(RuntimeError):
    pass


def _language_instruction(language: str) -> str:
    normalized = (language or "en").strip().lower()
    if normalized in {"ko", "kr", "korean", "한국어"}:
        return "Target language: Korean only. Write every lyric line in Korean. Do not write English lyric lines."
    if normalized in {"mixed", "ko-en", "en-ko", "bilingual", "혼합"}:
        return "Target language: Korean-English mixed. Blend Korean and English naturally in the lyrics."
    return "Target language: English only. Write every lyric line in English. Do not write Korean lyric lines."


def _build_prompt(
    theme: str | None,
    language: str,
    style: str | None,
    instruction: str | None,
    version_count: int,
) -> str:
    parts = [
        "Write a fresh lyric draft from scratch.",
        "Do not reuse or continue any previous draft.",
        f"Generate {version_count} candidate lyric version(s).",
    ]
    if theme:
        parts.append(f"Theme: {theme}")
    if style:
        parts.append(f"Style: {style}")
    if instruction:
        parts.append(f"Instruction: {instruction}")
    parts.append(_language_instruction(language))
    parts.append("Output rules: no explanation, no reasoning, no code fences, no markdown wrapper, no commentary.")
    parts.append("Use only the requested language in lyric lines.")
    parts.append("If you use sections, use short headings like [Verse 1], [Pre-Chorus], [Chorus], [Bridge], [Outro].")
    return "\n".join(parts)


def _clean_model_content(content: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    fence_match = re.fullmatch(r"```(?:markdown|md)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    return cleaned


def _build_messages(
    *,
    theme: str | None,
    language: str,
    style: str | None,
    instruction: str | None,
    version_count: int,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "\n".join(
                [
                    "You are a strict lyric generation engine.",
                    "Return only the lyric text.",
                    "Do not output reasoning, analysis, summaries, or code fences.",
                    "Do not mention previous drafts or internal thinking.",
                ]
            ),
        },
        {
            "role": "user",
            "content": _build_prompt(
                theme=theme,
                language=language,
                style=style,
                instruction=instruction,
                version_count=version_count,
            ),
        },
    ]


def generate_lyrics(
    *,
    model: str | None,
    theme: str | None,
    language: str,
    style: str | None,
    instruction: str | None,
    version_count: int = 1,
) -> str:
    selected_model = model or OLLAMA_MODEL
    payload = {
        "model": selected_model,
        "messages": _build_messages(
            theme=theme,
            language=language,
            style=style,
            instruction=instruction,
            version_count=version_count,
        ),
        "stream": False,
    }

    req = request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=OLLAMA_TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise OllamaServiceError(f"Failed to reach Ollama at {OLLAMA_URL}: {exc}") from exc

    content = body.get("message", {}).get("content")
    if not content:
        raise OllamaServiceError("Ollama response did not include message.content")

    return _clean_model_content(content)

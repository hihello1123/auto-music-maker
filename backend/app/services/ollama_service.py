import json
from urllib import error, request

from app.config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL


class OllamaServiceError(RuntimeError):
    pass


def _build_prompt(
    theme: str | None,
    language: str,
    style: str | None,
    instruction: str | None,
    version_count: int,
) -> str:
    parts = [
        "You are a lyric writer.",
        f"Language: {language}",
        f"Generate {version_count} candidate lyric versions.",
    ]
    if theme:
        parts.append(f"Theme: {theme}")
    if style:
        parts.append(f"Style: {style}")
    if instruction:
        parts.append(f"Instruction: {instruction}")
    parts.append("Return markdown only.")
    return "\n".join(parts)


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
    prompt = _build_prompt(theme, language, style, instruction, version_count)
    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
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

    return content.strip()

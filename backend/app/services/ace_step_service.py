import os
import json
import shlex
import subprocess
import time
from pathlib import Path
from urllib import request

from app.config import ACE_STEP_API_KEY, ACE_STEP_API_MODEL, ACE_STEP_API_POLL_INTERVAL, ACE_STEP_API_URL, ACE_STEP_CMD_TEMPLATE, ACE_STEP_TIMEOUT
from app.models.music import MusicGenerateRequest
from app.models.prompt_preset import PromptPreset


def build_blueprint_prompt(
    *,
    lyrics_content: str,
    request_data: MusicGenerateRequest,
    project_title: str,
    project_theme: str | None,
    prompt_preset: PromptPreset | None = None,
) -> str:
    parts = [
        "You are shaping a production-ready song blueprint for a local AI song studio.",
        "Return concise metadata and a polished song caption only.",
        "Preserve the original lyric meaning and do not invent unrelated story details.",
        f"Project: {project_title}",
    ]
    if project_theme:
        parts.append(f"Theme: {project_theme}")
    if request_data.genre:
        parts.append(f"Genre: {request_data.genre}")
    if request_data.mood:
        parts.append(f"Mood: {request_data.mood}")
    if request_data.bpm is not None:
        parts.append(f"Target BPM: {request_data.bpm}")
    if request_data.key:
        parts.append(f"Target Key: {request_data.key}")
    parts.append(f"Target Duration: {request_data.duration}s")
    parts.append(f"Mode: {request_data.mode}")
    parts.append(f"Song structure: {request_data.songStructure}")
    if request_data.songStructure == "chorus_only":
        parts.append("This is a short-form hook-first song, 30-60 seconds long, centered on the chorus.")
    if prompt_preset:
        parts.append(f"Preset: {prompt_preset.label}")
        if prompt_preset.blueprintGuidance:
            parts.append("Blueprint priorities:")
            parts.extend(f"- {line}" for line in prompt_preset.blueprintGuidance)
        if prompt_preset.avoidGuidance:
            parts.append("Avoid:")
            parts.extend(f"- {line}" for line in prompt_preset.avoidGuidance)
    parts.append("Lyrics:")
    parts.append(lyrics_content.strip())
    parts.append("Output fields: caption, lyrics, bpm, keyscale, duration, timesignature, language.")
    return "\n".join(parts)


def build_prompt(
    *,
    lyrics_content: str,
    request_data: MusicGenerateRequest,
    project_title: str,
    project_theme: str | None,
    prompt_preset: PromptPreset | None = None,
) -> str:
    parts = [
        "You are generating a polished, release-quality song demo for a local AI song studio.",
        "Follow the selected genre preset closely; it defines the arrangement, groove, and production texture.",
        "Focus on a memorable hook, emotional coherence, clean arrangement flow, and release-ready balance.",
        "Keep the arrangement intentional: every instrument should support the vocal and central hook.",
        "Avoid chaotic layering, abrupt genre switches, muddy low-end, and overly busy fills.",
        f"Project: {project_title}",
    ]
    if project_theme:
        parts.append(f"Theme: {project_theme}")
    if request_data.genre:
        parts.append(f"Genre: {request_data.genre}")
    if request_data.mood:
        parts.append(f"Mood: {request_data.mood}")
    if request_data.bpm is not None:
        parts.append(f"BPM: {request_data.bpm}")
    if request_data.key:
        parts.append(f"Key: {request_data.key}")
    if prompt_preset:
        parts.append(f"Preset: {prompt_preset.label}")
        if prompt_preset.generationGuidance:
            parts.append("Generation priorities:")
            parts.extend(f"- {line}" for line in prompt_preset.generationGuidance)
        if prompt_preset.avoidGuidance:
            parts.append("Avoid:")
            parts.extend(f"- {line}" for line in prompt_preset.avoidGuidance)
    if request_data.songStructure == "chorus_only":
        parts.append("Structure target: chorus-first short form, approximately 30-60 seconds.")
        parts.append("Emphasize one strong chorus hook and keep verses minimal or omitted.")
    parts.append(f"Duration: {request_data.duration}s")
    parts.append(f"Count: {request_data.count}")
    parts.append(f"Mode: {request_data.mode}")
    parts.append(f"Instrumental only: {request_data.instrumentalOnly}")
    parts.append(f"No additional vocals: {request_data.noAdditionalVocals}")
    parts.append(f"Preserve melody: {request_data.preserveMelody}")
    parts.append("Lyrics:")
    parts.append(lyrics_content.strip())
    parts.append("Aim for a strong singable refrain that matches the selected genre preset.")
    return "\n".join(parts)


def has_configured_runner() -> bool:
    return bool(ACE_STEP_CMD_TEMPLATE.strip())


def has_configured_api() -> bool:
    return bool(ACE_STEP_API_URL.strip())


def build_command(
    *,
    prompt_file: Path,
    output_dir: Path,
    request_data: MusicGenerateRequest,
) -> list[str]:
    if not has_configured_runner():
        raise ValueError("ACE_STEP_CMD_TEMPLATE is not configured")

    command = ACE_STEP_CMD_TEMPLATE.format(
        prompt_file=str(prompt_file),
        output_dir=str(output_dir),
        seed=request_data.seed if request_data.seed is not None else "",
        count=request_data.count,
        duration=request_data.duration,
        mode=request_data.mode,
        instrumental_only=str(request_data.instrumentalOnly).lower(),
        no_additional_vocals=str(request_data.noAdditionalVocals).lower(),
        preserve_melody=str(request_data.preserveMelody).lower(),
        lyric_file=str(prompt_file),
    )
    return shlex.split(command)


def execute_runner(command: list[str], cwd: Path | None = None) -> None:
    env = os.environ.copy()
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=ACE_STEP_TIMEOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "ACE-Step command failed: "
            f"{' '.join(command)}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def _api_url(path: str) -> str:
    return ACE_STEP_API_URL.rstrip("/") + path


def _http_json(method: str, path: str, payload: dict | None = None) -> dict:
    body = None
    headers = {"Content-Type": "application/json"}
    if ACE_STEP_API_KEY.strip():
        headers["Authorization"] = f"Bearer {ACE_STEP_API_KEY.strip()}"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(_api_url(path), data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=ACE_STEP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def submit_generation_task(
    *,
    prompt: str,
    lyrics: str,
    request_data: MusicGenerateRequest,
    music_plan: dict | None = None,
) -> str:
    if not has_configured_api():
        raise ValueError("ACE_STEP_API_URL is not configured")

    plan = music_plan or {}
    payload: dict[str, object] = {
        "prompt": prompt.strip() or str(plan.get("caption") or ""),
        "lyrics": lyrics.strip() or str(plan.get("lyrics") or ""),
        "audio_duration": plan.get("duration") or request_data.duration,
        "batch_size": max(1, request_data.count),
        "use_random_seed": request_data.seed is None,
        "task_type": "text2music",
        "thinking": False,
    }
    if request_data.seed is not None:
        payload["seed"] = request_data.seed
    if plan.get("bpm") is not None:
        payload["bpm"] = plan.get("bpm")
    elif request_data.bpm is not None:
        payload["bpm"] = request_data.bpm
    key_value = plan.get("key") or plan.get("keyScale")
    if key_value:
        payload["key_scale"] = key_value
    elif request_data.key:
        payload["key_scale"] = request_data.key
    if plan.get("genre"):
        payload["genres"] = plan.get("genre")
    elif request_data.genre:
        payload["genres"] = request_data.genre
    if request_data.instrumentalOnly:
        payload["instrumental_only"] = True
    if request_data.noAdditionalVocals:
        payload["no_additional_vocals"] = True
    if request_data.preserveMelody:
        payload["preserve_melody"] = True
    if plan.get("language"):
        payload["vocal_language"] = plan.get("language")
    if ACE_STEP_API_MODEL.strip():
        payload["model"] = ACE_STEP_API_MODEL.strip()

    response = _http_json("POST", "/release_task", payload)
    task_id = response.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"ACE-Step API did not return a task_id: {response}")
    return str(task_id)


def poll_generation_task(task_id: str) -> dict:
    if not has_configured_api():
        raise ValueError("ACE_STEP_API_URL is not configured")

    deadline = time.monotonic() + ACE_STEP_TIMEOUT
    while time.monotonic() < deadline:
        response = _http_json("POST", "/query_result", {"task_id_list": [task_id]})
        items = response.get("data") or []
        if not items:
            time.sleep(ACE_STEP_API_POLL_INTERVAL)
            continue

        item = items[0]
        status = item.get("status")
        if status in (1, 2):
            return item

        time.sleep(ACE_STEP_API_POLL_INTERVAL)

    raise TimeoutError(f"ACE-Step task {task_id} did not finish within {ACE_STEP_TIMEOUT} seconds")


def download_audio_url(audio_url: str, destination: Path) -> None:
    if audio_url.startswith("http://") or audio_url.startswith("https://"):
        download_url = audio_url
    elif audio_url.startswith("/"):
        download_url = ACE_STEP_API_URL.rstrip("/") + audio_url
    else:
        download_url = ACE_STEP_API_URL.rstrip("/") + "/" + audio_url.lstrip("/")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with request.urlopen(download_url, timeout=ACE_STEP_TIMEOUT) as resp, destination.open("wb") as file:
        file.write(resp.read())


def extract_audio_urls(task_result: dict) -> list[str]:
    raw_result = task_result.get("result")
    if raw_result is None:
        return []
    if isinstance(raw_result, str):
        try:
            parsed = json.loads(raw_result)
        except json.JSONDecodeError:
            return []
    else:
        parsed = raw_result
    if not isinstance(parsed, list):
        return []

    urls: list[str] = []
    for item in parsed:
        if isinstance(item, dict):
            file_url = item.get("file")
            if isinstance(file_url, str) and file_url:
                urls.append(file_url)
    return urls


def generate_music_blueprint(
    *,
    prompt: str,
    lyrics: str,
    request_data: MusicGenerateRequest,
) -> dict:
    if not has_configured_api():
        raise ValueError("ACE_STEP_API_URL is not configured")

    param_obj: dict[str, object] = {}
    if request_data.bpm is not None:
        param_obj["bpm"] = request_data.bpm
    if request_data.key:
        param_obj["key"] = request_data.key
    param_obj["duration"] = request_data.duration
    if request_data.genre:
        param_obj["genres"] = request_data.genre

    payload: dict[str, object] = {
        "prompt": prompt,
        "lyrics": lyrics,
        "param_obj": param_obj,
    }
    response = _http_json("POST", "/format_input", payload)
    data = response.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"ACE-Step format_input did not return a blueprint: {response}")
    return data

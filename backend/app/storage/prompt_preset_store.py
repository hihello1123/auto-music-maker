import json
from pathlib import Path

from app.models.prompt_preset import PromptPreset

PRESETS_DIR = Path(__file__).resolve().parents[2] / "data" / "prompt_presets"


def _preset_files() -> list[Path]:
    if not PRESETS_DIR.exists():
        return []
    return sorted(path for path in PRESETS_DIR.iterdir() if path.suffix.lower() == ".json")


def list_prompt_presets() -> list[PromptPreset]:
    presets: list[PromptPreset] = []
    for path in _preset_files():
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        presets.append(PromptPreset(**data))
    return presets


def get_prompt_preset(preset_id: str) -> PromptPreset | None:
    for preset in list_prompt_presets():
        if preset.id == preset_id:
            return preset
    return None


def save_prompt_preset(preset: PromptPreset) -> PromptPreset:
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = PRESETS_DIR / f"{preset.id}.json"
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(preset.model_dump(), file, ensure_ascii=False, indent=2, default=str)
    return preset

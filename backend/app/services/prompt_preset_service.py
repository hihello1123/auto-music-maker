import re
from datetime import datetime

from app.models.prompt_preset import PromptPreset
from app.storage import prompt_preset_store

PRESET_ALIASES = {
    "emotional_pop_ballad": "pop_ballad",
    "indie_ballad": "indie_pop",
    "rnb_soul_ballad": "rnb_soul",
    "jazz_bar_ballad": "jazz",
    "city_pop_night": "city_pop",
    "acoustic_folk_ballad": "acoustic_folk",
    "cinematic_ballad": "orchestral_pop",
    "soft_pop_shortform": "synth_pop",
}


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def list_prompt_presets() -> list[PromptPreset]:
    return prompt_preset_store.list_prompt_presets()


def get_prompt_preset(preset_id: str) -> PromptPreset | None:
    return prompt_preset_store.get_prompt_preset(preset_id)


def resolve_prompt_preset(genre: str | None = None, preset_id: str | None = None) -> PromptPreset:
    presets = list_prompt_presets()
    if not presets:
        return PromptPreset(
            id="default",
            label="Default",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )

    if preset_id:
        preset = get_prompt_preset(PRESET_ALIASES.get(preset_id, preset_id))
        if preset:
            return preset

    normalized_genre = _normalize(genre)
    if normalized_genre:
        for preset in presets:
            if _normalize(preset.id) == normalized_genre:
                return preset
            if any(_normalize(match) == normalized_genre for match in preset.matchGenres):
                return preset

    for preset in presets:
        if preset.id == "default":
            return preset

    return presets[0]

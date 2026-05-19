from fastapi import APIRouter, HTTPException

from app.models.prompt_preset import PromptPreset
from app.services import prompt_preset_service

router = APIRouter(prefix="/prompt-presets", tags=["prompt-presets"])


@router.get("", response_model=list[PromptPreset])
def list_prompt_presets():
    return prompt_preset_service.list_prompt_presets()


@router.get("/{preset_id}", response_model=PromptPreset)
def get_prompt_preset(preset_id: str):
    preset = prompt_preset_service.get_prompt_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Prompt preset {preset_id} not found")
    return preset

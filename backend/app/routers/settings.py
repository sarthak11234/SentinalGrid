"""
Settings API — model selection and configuration.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


class ModelListResponse(BaseModel):
    current_model: str
    available_models: list[str]


class ModelUpdateRequest(BaseModel):
    model: str


@router.get("/models", response_model=ModelListResponse)
async def get_models():
    """Get the current model and list of available Gemini models."""
    settings = get_settings()
    return {
        "current_model": settings.gemini_model,
        "available_models": settings.available_models,
    }


@router.post("/models")
async def set_model(req: ModelUpdateRequest):
    """
    Update the active Gemini model for this session.
    Note: In a production app, this would be per-user in the DB.
    For the prototype, we update the cached settings object.
    """
    settings = get_settings()

    if req.model not in settings.available_models:
        return {"error": f"Model '{req.model}' is not available", "available": settings.available_models}

    # Update the cached settings (prototype approach — not persistent across restarts)
    settings.gemini_model = req.model
    return {"message": f"Model updated to {req.model}", "current_model": req.model}

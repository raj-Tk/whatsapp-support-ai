from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.chat import Category


class CategoryThresholdResponse(BaseModel):
    id: str
    category: str
    threshold: float
    automation_enabled: bool
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class CategoryThresholdUpdate(BaseModel):
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    automation_enabled: bool | None = None


class CategoryThresholdSeed(BaseModel):
    category: Category
    threshold: float = Field(..., ge=0.0, le=1.0)
    automation_enabled: bool

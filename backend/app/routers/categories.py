from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CategoryThreshold
from app.schemas.category_threshold import (
    CategoryThresholdResponse,
    CategoryThresholdUpdate,
)
from app.schemas.chat import Category


router = APIRouter(prefix="/categories", tags=["Category Thresholds"])


@router.get("/thresholds", response_model=list[CategoryThresholdResponse])
def list_category_thresholds(db: Session = Depends(get_db)):
    return db.query(CategoryThreshold).order_by(CategoryThreshold.category.asc()).all()


@router.patch("/thresholds/{category}", response_model=CategoryThresholdResponse)
def update_category_threshold(
    category: Category,
    payload: CategoryThresholdUpdate,
    db: Session = Depends(get_db),
):
    threshold = (
        db.query(CategoryThreshold)
        .filter(CategoryThreshold.category == category)
        .first()
    )
    if threshold is None:
        raise HTTPException(status_code=404, detail="Category threshold not found")

    if payload.threshold is not None:
        threshold.threshold = payload.threshold
    if payload.automation_enabled is not None:
        threshold.automation_enabled = payload.automation_enabled

    threshold.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(threshold)

    return threshold

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification, User
from app.schemas.notification import NotificationResponse, NotificationStatusUpdate


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/user/{user_id}", response_model=list[NotificationResponse])
def list_user_notifications(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return (
        db.query(Notification)
        .filter(Notification.recipient_id == user_id)
        .order_by(Notification.sent_at.desc().nullslast())
        .all()
    )


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification_status(
    notification_id: str,
    payload: NotificationStatusUpdate,
    db: Session = Depends(get_db),
):
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    if payload.status not in {"pending", "sent", "read", "failed"}:
        raise HTTPException(status_code=400, detail="Invalid notification status")

    notification.status = payload.status
    if payload.status in {"sent", "read"} and notification.sent_at is None:
        notification.sent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(notification)

    return notification

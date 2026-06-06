from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    recipient_id: str
    ticket_id: str | None = None
    channel: str
    message: str
    status: str
    sent_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class NotificationStatusUpdate(BaseModel):
    status: str

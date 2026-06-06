from datetime import datetime

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    id: str
    ticket_id: str | None = None
    sender_id: str
    message: str
    message_type: str
    classification: str | None = None
    confidence: float | None = None
    timestamp: datetime

    model_config = {
        "from_attributes": True,
    }


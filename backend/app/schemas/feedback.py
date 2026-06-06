from datetime import datetime
from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    agent_id: str
    suggested_category: str
    actual_category: str
    automation_suggested: bool = False
    automation_approved: bool = False


class FeedbackResponse(FeedbackRequest):
    id: str
    ticket_id: str
    timestamp: datetime

    model_config = {
        "from_attributes": True,
    }
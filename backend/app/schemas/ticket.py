from datetime import datetime
from pydantic import BaseModel


class TicketResponse(BaseModel):
    id: str
    user_id: str
    category: str
    raw_message: str
    confidence: float
    status: str
    priority: str
    automation_eligible: bool
    escalation_flag: bool
    assigned_agent_id: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None
    resolution_notes: str | None = None

    model_config = {
        "from_attributes": True,
    }


class TicketClaimRequest(BaseModel):
    agent_id: str


class TicketResolveRequest(BaseModel):
    resolution_notes: str


class TicketEscalateRequest(BaseModel):
    supervisor_id: str | None = None
    reason: str

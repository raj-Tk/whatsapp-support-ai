from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_users: int
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    escalated_tickets: int
    automation_rate: float
    average_confidence: float
    feedback_count: int
    automation_approved_count: int
    automation_rejected_count: int
    category_breakdown: dict[str, int]
    agent_workload: dict[str, int]


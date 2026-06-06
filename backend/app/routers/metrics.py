from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AgentFeedback, Ticket, User
from app.schemas import MetricsResponse


router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary", response_model=MetricsResponse)
def get_summary_metrics(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "open").count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == "in_progress").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved").count()
    escalated_tickets = db.query(Ticket).filter(Ticket.escalation_flag.is_(True)).count()
    auto_eligible_tickets = (
        db.query(Ticket).filter(Ticket.automation_eligible.is_(True)).count()
    )
    feedback_count = db.query(AgentFeedback).count()
    automation_approved_count = (
        db.query(AgentFeedback)
        .filter(AgentFeedback.automation_approved.is_(True))
        .count()
    )
    automation_rejected_count = feedback_count - automation_approved_count

    average_confidence = db.query(func.avg(Ticket.confidence)).scalar() or 0
    automation_rate = auto_eligible_tickets / total_tickets if total_tickets else 0

    category_rows = (
        db.query(Ticket.category, func.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )
    workload_rows = (
        db.query(Ticket.assigned_agent_id, func.count(Ticket.id))
        .filter(Ticket.assigned_agent_id.is_not(None))
        .group_by(Ticket.assigned_agent_id)
        .all()
    )

    return MetricsResponse(
        total_users=total_users,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets,
        escalated_tickets=escalated_tickets,
        automation_rate=round(automation_rate, 2),
        average_confidence=round(float(average_confidence), 2),
        feedback_count=feedback_count,
        automation_approved_count=automation_approved_count,
        automation_rejected_count=automation_rejected_count,
        category_breakdown={category: count for category, count in category_rows},
        agent_workload={agent_id: count for agent_id, count in workload_rows},
    )


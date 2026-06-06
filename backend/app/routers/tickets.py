from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AgentFeedback, Notification, Ticket, User
from app.schemas.ticket import (
    TicketClaimRequest,
    TicketEscalateRequest,
    TicketResolveRequest,
    TicketResponse,
)
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/claim", response_model=TicketResponse)
def claim_ticket(
    ticket_id: str,
    payload: TicketClaimRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = db.get(User, payload.agent_id)
    if agent is None or agent.role not in {"agent", "supervisor", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid agent")

    ticket.assigned_agent_id = payload.agent_id
    ticket.status = "in_progress"

    notification = Notification(
        recipient_id=payload.agent_id,
        ticket_id=ticket.id,
        channel="in_app",
        message=f"You claimed ticket {ticket.id}.",
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.patch("/{ticket_id}/resolve", response_model=TicketResponse)
def resolve_ticket(
    ticket_id: str,
    payload: TicketResolveRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = "resolved"
    ticket.resolved_at = datetime.now(timezone.utc)
    ticket.resolution_notes = payload.resolution_notes

    notification = Notification(
        recipient_id=ticket.user_id,
        ticket_id=ticket.id,
        channel="in_app",
        message=f"Ticket {ticket.id} has been resolved. {payload.resolution_notes}",
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.patch("/{ticket_id}/escalate", response_model=TicketResponse)
def escalate_ticket(
    ticket_id: str,
    payload: TicketEscalateRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    supervisor_id = payload.supervisor_id

    if supervisor_id is None:
        supervisor = db.query(User).filter(User.role == "supervisor").first()
        if supervisor is None:
            raise HTTPException(status_code=400, detail="No supervisor available")
        supervisor_id = supervisor.id
    else:
        supervisor = db.get(User, supervisor_id)
        if supervisor is None or supervisor.role != "supervisor":
            raise HTTPException(status_code=400, detail="Invalid supervisor")

    ticket.assigned_agent_id = supervisor_id
    ticket.status = "escalated"
    ticket.escalation_flag = True
    ticket.priority = "high"
    ticket.resolution_notes = payload.reason

    notification = Notification(
        recipient_id=supervisor_id,
        ticket_id=ticket.id,
        channel="in_app",
        message=f"Ticket {ticket.id} escalated. Reason: {payload.reason}",
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.post("/{ticket_id}/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    ticket_id: str,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = db.get(User, payload.agent_id)
    if agent is None or agent.role not in {"agent", "supervisor", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid agent")

    feedback = AgentFeedback(
        ticket_id=ticket_id,
        agent_id=payload.agent_id,
        suggested_category=payload.suggested_category,
        actual_category=payload.actual_category,
        automation_suggested=payload.automation_suggested,
        automation_approved=payload.automation_approved,
    )
    db.add(feedback)

    if payload.automation_approved:
        ticket.status = "resolved"
        ticket.resolution_notes = payload.actual_category
    else:
        ticket.status = "open"

    db.commit()
    db.refresh(feedback)

    return feedback

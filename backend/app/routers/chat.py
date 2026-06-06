from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Ticket, Conversation, Notification
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services import classify_message, decide_next_action, auto_resolve
from app.websocket import connection_manager

router = APIRouter(prefix="/chat", tags=["Chat"])


def _assign_agent(db: Session, escalation: bool = False) -> str | None:
    if escalation:
        supervisor = db.query(User).filter(User.role == "supervisor").first()
        if supervisor:
            return supervisor.id

    agent = db.query(User).filter(User.role == "agent").first()
    if agent:
        return agent.id

    admin = db.query(User).filter(User.role == "admin").first()
    return admin.id if admin else None


@router.post("/", response_model=ChatMessageResponse)
async def process_chat(payload: ChatMessageRequest, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    classification = classify_message(payload.message)
    decision, reason = decide_next_action(classification)

    ticket_id = None
    assigned_agent_id = None

    if decision == "auto_resolve":
        system_response = auto_resolve(db, user, classification)
    else:
        assigned_agent_id = _assign_agent(
            db,
            escalation=(
                classification.escalation_signals
                or classification.primary_category == "Escalation"
            ),
        )

        ticket = Ticket(
            user_id=user.id,
            category=classification.primary_category,
            raw_message=payload.message,
            confidence=classification.overall_confidence,
            automation_eligible=False,
            escalation_flag=classification.escalation_signals
            or classification.primary_category == "Escalation",
            assigned_agent_id=assigned_agent_id,
            priority="high"
            if classification.escalation_signals
            or classification.frustration_level in {"high", "extreme"}
            else "medium",
        )
        db.add(ticket)
        db.flush()

        ticket_id = ticket.id

        system_response = (
            f"Your request requires a human agent. Ticket {ticket.id} has been created. "
            f"Reason: {reason}"
        )

        if assigned_agent_id:
            notification = Notification(
                recipient_id=assigned_agent_id,
                ticket_id=ticket.id,
                channel="in_app",
                message=f"New ticket {ticket.id} assigned. Reason: {reason}",
                status="sent",
                sent_at=datetime.now(timezone.utc),
            )
            db.add(notification)

    user_message = Conversation(
        ticket_id=ticket_id,
        sender_id=user.id,
        message=payload.message,
        message_type="user",
        classification=classification.primary_category,
        confidence=classification.overall_confidence,
    )
    db.add(user_message)
    db.flush()

    system_message = Conversation(
        ticket_id=ticket_id,
        sender_id=user.id,
        message=system_response,
        message_type="system",
        classification=classification.primary_category,
        confidence=classification.overall_confidence,
    )
    db.add(system_message)
    db.flush()

    db.commit()
    db.refresh(user_message)
    db.refresh(system_message)

    response = ChatMessageResponse(
        message_id=user_message.id,
        classification=classification,
        decision=decision,
        ticket_id=ticket_id,
        system_response=system_response,
    )

    await connection_manager.send_to_user(
        user.id,
        {
            "event": "chat.processed",
            "user_message": {
                "id": user_message.id,
                "message": user_message.message,
                "message_type": user_message.message_type,
            },
            "system_message": {
                "id": system_message.id,
                "message": system_message.message,
                "message_type": system_message.message_type,
            },
            "classification": classification.model_dump(),
            "decision": decision,
            "ticket_id": ticket_id,
        },
    )

    if assigned_agent_id:
        await connection_manager.send_to_user(
            assigned_agent_id,
            {
                "event": "ticket.assigned",
                "ticket_id": ticket_id,
                "customer_id": user.id,
                "customer_name": user.name,
                "category": classification.primary_category,
                "confidence": classification.overall_confidence,
                "message": payload.message,
                "system_response": system_response,
            },
        )

    return response

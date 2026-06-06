from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Ticket, User
from app.schemas import ConversationResponse


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/ticket/{ticket_id}", response_model=list[ConversationResponse])
def list_ticket_conversation(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return (
        db.query(Conversation)
        .filter(Conversation.ticket_id == ticket_id)
        .order_by(Conversation.timestamp.asc())
        .all()
    )


@router.get("/user/{user_id}", response_model=list[ConversationResponse])
def list_user_conversation(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return (
        db.query(Conversation)
        .filter(Conversation.sender_id == user_id)
        .order_by(Conversation.timestamp.asc())
        .all()
    )


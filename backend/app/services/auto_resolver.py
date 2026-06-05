from datetime import date

from sqlalchemy.orm import Session

from app.models import Attendance, Invoice, User
from app.schemas import ClassificationResult


def auto_resolve(
    db: Session,
    user: User,
    classification: ClassificationResult,
) -> str:
    category = classification.primary_category

    if category == "Attendance Request":
        return resolve_attendance(db, user)

    if category == "Billing Inquiry":
        return resolve_billing(db, user)

    if category == "General FAQ":
        return resolve_faq()

    return "This issue cannot be auto-resolved and requires human support."


def resolve_attendance(db: Session, user: User) -> str:
    today = date.today()

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user.id,
            Attendance.date == today,
        )
        .first()
    )

    if existing is None:
        attendance = Attendance(
            user_id=user.id,
            date=today,
            status="present",
            marked_by="system",
        )
        db.add(attendance)
    else:
        existing.status = "present"
        existing.marked_by = "system"

    return (
        f"Hi {user.name}, your attendance has been marked as Present for today. "
        "Have a productive day!"
    )


def resolve_billing(db: Session, user: User) -> str:
    invoice = (
        db.query(Invoice)
        .filter(Invoice.user_id == user.id)
        .order_by(Invoice.created_at.desc())
        .first()
    )

    if invoice is None:
        return (
            f"Hi {user.name}, I could not find an invoice for your account. "
            "I've created a support request so an agent can help you."
        )

    return (
        f"Hi {user.name}, your latest invoice {invoice.id} for Rs. {invoice.amount} "
        f"is {invoice.status}. Due date: {invoice.due_date}. "
        f"Download: {invoice.file_url or 'Not available'}"
    )


def resolve_faq() -> str:
    return (
        "To reset your password: go to Settings > Security, choose Forgot Password, "
        "enter your registered email, and follow the reset link sent to your inbox."
    )
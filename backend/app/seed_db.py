from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models import Invoice, User


def seed_users(db):
    users = [
        User(
            id="USR-101",
            name="Priya Sharma",
            phone="+919000000101",
            email="priya@example.com",
            role="customer",
            department=None,
        ),
        User(
            id="USR-205",
            name="Rohit Mehta",
            phone="+919000000205",
            email="rohit@example.com",
            role="customer",
            department=None,
        ),
        User(
            id="USR-312",
            name="Anjali Patel",
            phone="+919000000312",
            email="anjali@example.com",
            role="customer",
            department=None,
        ),
        User(
            id="AGT-201",
            name="Karan Verma",
            phone="+919000001201",
            email="karan.agent@example.com",
            role="agent",
            department="Support",
        ),
        User(
            id="AGT-202",
            name="Neha Singh",
            phone="+919000001202",
            email="neha.agent@example.com",
            role="agent",
            department="Technical Support",
        ),
        User(
            id="SUP-301",
            name="Meera Iyer",
            phone="+919000001301",
            email="meera.supervisor@example.com",
            role="supervisor",
            department="Support",
        ),
        User(
            id="ADM-401",
            name="Admin User",
            phone="+919000001401",
            email="admin@example.com",
            role="admin",
            department="Operations",
        ),
    ]

    for user in users:
        existing = db.get(User, user.id) # This script is idempotent. means it will not dublicate user/invoices. this is the function 

        if existing is None:
            db.add(user)


def seed_invoices(db):
    invoices = [
        Invoice(
            id="INV-2024-089",
            user_id="USR-205",
            amount=Decimal("4500.00"),
            due_date=date(2025, 1, 15),
            status="pending",
            file_url="https://example.com/invoices/INV-2024-089.pdf",
        ),
        Invoice(
            id="INV-2024-102",
            user_id="USR-312",
            amount=Decimal("7200.00"),
            due_date=date(2025, 1, 20),
            status="overdue",
            file_url="https://example.com/invoices/INV-2024-102.pdf",
        ),
    ]

    for invoice in invoices:
        existing = db.get(Invoice, invoice.id)
        if existing is None:
            db.add(invoice)


def seed_db():
    db = SessionLocal()
    try:
        seed_users(db)
        db.commit()

        seed_invoices(db)
        db.commit()

        print("Database seeded successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
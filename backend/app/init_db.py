from app.database import Base, engine
from app.models import (
    AgentFeedback,
    Attendance,
    CategoryThreshold,
    Conversation,
    Invoice,
    Notification,
    Ticket,
    User,
)


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")

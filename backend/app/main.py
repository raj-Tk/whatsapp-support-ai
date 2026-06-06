from fastapi import FastAPI

from app.routers import users
from app.routers.chat import router as chat_router
from app.routers.conversations import router as conversations_router
from app.routers.metrics import router as metrics_router
from app.routers.notifications import router as notifications_router
from app.routers.realtime import router as realtime_router
from app.routers.tickets import router as tickets_router

app = FastAPI(
    title="WhatsApp Support Automation System",
    description="AI-powered support automation system with ticket routing, auto-resolution, and feedback learning.",
    version="1.0.0",
)

app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(metrics_router)
app.include_router(notifications_router)
app.include_router(realtime_router)
app.include_router(tickets_router)
app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "WhatsApp Support Automation API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "whatsapp-support-api",
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(categories_router)
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

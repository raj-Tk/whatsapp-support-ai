from fastapi import FastAPI

from app.routers import users

app = FastAPI(
    title="WhatsApp Support Automation System",
    description="AI-powered support automation system with ticket routing, auto-resolution, and feedback learning.",
    version="1.0.0",
)

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
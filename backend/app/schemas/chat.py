from typing import Literal

from pydantic import BaseModel, Field


Category = Literal[
    "Attendance Request",
    "Billing Inquiry",
    "Account Access",
    "Technical Glitch",
    "Complaint",
    "Feature Request",
    "General FAQ",
    "Escalation",
]

Language = Literal["english", "hindi", "hinglish", "unknown"]
FrustrationLevel = Literal["low", "medium", "high", "extreme"]
DecisionType = Literal["auto_resolve", "human_required"]


class ChatMessageRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1)


class ClassificationResult(BaseModel):
    primary_category: Category
    all_categories: list[Category]
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sarcasm_detected: bool
    frustration_level: FrustrationLevel
    escalation_signals: bool
    language: Language
    requires_human: bool
    requires_human_reason: str = ""


class ChatMessageResponse(BaseModel):
    message_id: str
    classification: ClassificationResult
    decision: DecisionType
    ticket_id: str | None = None
    system_response: str
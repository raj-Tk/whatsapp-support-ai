from sqlalchemy.orm import Session

from app.config import settings
from app.models import CategoryThreshold
from app.schemas import ClassificationResult


AUTOMATABLE_CATEGORIES = {
    "Attendance Request",
    "Billing Inquiry",
    "General FAQ",
}


def get_category_policy(
    classification: ClassificationResult,
    db: Session | None = None,
) -> tuple[float, bool]:
    if db is None:
        return (
            settings.confidence_threshold,
            classification.primary_category in AUTOMATABLE_CATEGORIES,
        )

    policy = (
        db.query(CategoryThreshold)
        .filter(CategoryThreshold.category == classification.primary_category)
        .first()
    )
    if policy is None:
        return (
            settings.confidence_threshold,
            classification.primary_category in AUTOMATABLE_CATEGORIES,
        )

    return policy.threshold, policy.automation_enabled


def decide_next_action(
    classification: ClassificationResult,
    db: Session | None = None,
) -> tuple[str, str]:
    threshold, automation_enabled = get_category_policy(classification, db)

    if classification.overall_confidence < threshold:
        return (
            "human_required",
            f"Confidence is below the category threshold ({threshold:.0%}).",
        )

    if classification.escalation_signals:
        return (
            "human_required",
            "Escalation signal detected.",
        )

    if classification.sarcasm_detected:
        return (
            "human_required",
            "Sarcasm detected; human review required.",
        )

    if classification.frustration_level in {"high", "extreme"}:
        return (
            "human_required",
            "High frustration detected.",
        )

    if classification.requires_human:
        return (
            "human_required",
            classification.requires_human_reason or "Classifier requested human review.",
        )

    if len(classification.all_categories) > 1:
        return (
            "human_required",
            "Multi-issue message requires human review.",
        )

    if not automation_enabled:
        return (
            "human_required",
            "Automation is disabled for this category.",
        )

    return (
        "auto_resolve",
        "Category automation is enabled and confidence is above threshold.",
    )

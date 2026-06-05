from app.config import settings
from app.schemas import ClassificationResult


AUTOMATABLE_CATEGORIES = {
    "Attendance Request",
    "Billing Inquiry",
    "General FAQ",
}


def decide_next_action(classification: ClassificationResult) -> tuple[str, str]:
    if classification.overall_confidence < settings.confidence_threshold:
        return (
            "human_required",
            "Confidence is below the automation threshold.",
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

    if classification.primary_category not in AUTOMATABLE_CATEGORIES:
        return (
            "human_required",
            "Category is not eligible for automation.",
        )

    return (
        "auto_resolve",
        "Category is eligible for automation and confidence is above threshold.",
    )
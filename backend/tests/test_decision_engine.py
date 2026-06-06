from app.schemas import ClassificationResult
from app.services.decision_engine import decide_next_action


def make_classification(**overrides):
    data = {
        "primary_category": "Attendance Request",
        "all_categories": ["Attendance Request"],
        "overall_confidence": 0.95,
        "sentiment_score": 0.0,
        "sarcasm_detected": False,
        "frustration_level": "low",
        "escalation_signals": False,
        "language": "english",
        "requires_human": False,
        "requires_human_reason": "",
    }
    data.update(overrides)
    return ClassificationResult.model_validate(data)


def test_auto_resolve_when_confident_and_eligible():
    decision, _ = decide_next_action(make_classification())

    assert decision == "auto_resolve"


def test_human_required_for_sarcasm():
    decision, reason = decide_next_action(
        make_classification(
            primary_category="Complaint",
            all_categories=["Complaint"],
            sarcasm_detected=True,
            frustration_level="high",
        )
    )

    assert decision == "human_required"
    assert "Sarcasm" in reason


def test_human_required_for_multi_issue():
    decision, reason = decide_next_action(
        make_classification(
            all_categories=["Billing Inquiry", "Account Access", "Complaint"]
        )
    )

    assert decision == "human_required"
    assert "Multi-issue" in reason

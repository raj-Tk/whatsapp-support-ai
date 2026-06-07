from app.schemas import ClassificationResult
from app.services.decision_engine import decide_next_action


class FakeQuery:
    def __init__(self, policy):
        self.policy = policy

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.policy


class FakeDb:
    def __init__(self, policy):
        self.policy = policy

    def query(self, _model):
        return FakeQuery(self.policy)


class FakePolicy:
    threshold = 0.95
    automation_enabled = False


def make_classification(**overrides):
    data = {
        "primary_category": "Attendance Request",
        "all_categories": ["Attendance Request"],
        "overall_confidence": 0.90,
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


def test_category_threshold_blocks_low_confidence():
    decision, reason = decide_next_action(make_classification(), FakeDb(FakePolicy()))

    assert decision == "human_required"
    assert "threshold" in reason


def test_category_policy_can_disable_automation():
    decision, reason = decide_next_action(
        make_classification(overall_confidence=0.99),
        FakeDb(FakePolicy()),
    )

    assert decision == "human_required"
    assert "disabled" in reason

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import ClassificationResult
from app.services import classify_message, decide_next_action


KEYWORD_RULES = [
    ("Escalation", ["manager", "legal action", "unacceptable", "senior agent", "escalate"]),
    ("Technical Glitch", ["crash", "crashing", "error", "502", "upload"]),
    ("Complaint", ["ridiculous", "disappointed", "amazing", "waited", "nobody helped"]),
    ("Feature Request", ["add", "feature", "support bulk", "dark mode", "exported to excel"]),
    ("Account Access", ["login", "locked", "password", "reset link"]),
    ("Billing Inquiry", ["invoice", "payment", "refund", "amount", "due date", "paid"]),
    ("Attendance Request", ["attendance", "remote", "work from home", "wfh"]),
    ("General FAQ", ["how do i", "policy", "working hours", "where can i", "thanks"]),
]


def mock_classify(message: str) -> ClassificationResult:
    lower = message.lower()
    categories = []
    for category, keywords in KEYWORD_RULES:
        if any(keyword in lower for keyword in keywords):
            categories.append(category)

    if not categories:
        categories = ["General FAQ"]

    primary = categories[0]
    sarcasm = "amazing" in lower or "fantastic" in lower or "just what i needed" in lower
    escalation = any(word in lower for word in ["manager", "legal action", "unacceptable", "senior agent"])
    frustration = "high" if any(word in lower for word in ["ridiculous", "disappointed", "waited", "unacceptable"]) else "low"
    automatable = primary in {"Attendance Request", "Billing Inquiry", "General FAQ"}

    return ClassificationResult(
        primary_category=primary,
        all_categories=categories,
        overall_confidence=0.88,
        sentiment_score=-0.7 if sarcasm or frustration == "high" else 0.0,
        sarcasm_detected=sarcasm,
        frustration_level=frustration,
        escalation_signals=escalation,
        language="hinglish" if any(token in lower for token in ["kya", "hoon", "hai", "karta"]) else "english",
        requires_human=(not automatable) or len(categories) > 1 or sarcasm or escalation,
        requires_human_reason="Mock rule triggered human review" if ((not automatable) or len(categories) > 1 or sarcasm or escalation) else "",
    )


def evaluate(dataset_path: Path, live: bool) -> dict:
    rows = json.loads(dataset_path.read_text(encoding="utf-8"))
    total = len(rows)
    primary_matches = 0
    action_matches = 0
    results = []

    for row in rows:
        classification = classify_message(row["message"]) if live else mock_classify(row["message"])
        decision, reason = decide_next_action(classification)
        expected_action = row["expected_action"]
        primary_match = classification.primary_category == row["expected_primary_category"]
        action_match = decision == expected_action
        primary_matches += int(primary_match)
        action_matches += int(action_match)
        results.append(
            {
                "id": row["id"],
                "expected_primary": row["expected_primary_category"],
                "predicted_primary": classification.primary_category,
                "primary_match": primary_match,
                "expected_action": expected_action,
                "predicted_action": decision,
                "action_match": action_match,
                "reason": reason,
            }
        )

    return {
        "mode": "live_groq" if live else "mock_rules",
        "total": total,
        "primary_accuracy": round(primary_matches / total, 3) if total else 0,
        "action_accuracy": round(action_matches / total, 3) if total else 0,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate classifier against labelled dataset.")
    parser.add_argument("--dataset", default="../dataset/sample_conversations.json")
    parser.add_argument("--live", action="store_true", help="Use live Groq classifier instead of mock rules.")
    parser.add_argument("--output", default="evaluation_results.json")
    args = parser.parse_args()

    dataset_path = Path(args.dataset).resolve()
    report = evaluate(dataset_path, args.live)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()


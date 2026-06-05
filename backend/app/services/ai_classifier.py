import json

from groq import Groq

from app.config import settings
from app.schemas import ClassificationResult


SYSTEM_PROMPT = """
You are an AI classifier for a WhatsApp-style customer support automation system.

Analyze the customer message and return ONLY a valid JSON object.
No markdown. No explanation. No extra text.

Valid categories:
- Attendance Request
- Billing Inquiry
- Account Access
- Technical Glitch
- Complaint
- Feature Request
- General FAQ
- Escalation

Return this exact JSON shape:
{
  "primary_category": "Attendance Request",
  "all_categories": ["Attendance Request"],
  "overall_confidence": 0.95,
  "sentiment_score": 0.0,
  "sarcasm_detected": false,
  "frustration_level": "low",
  "escalation_signals": false,
  "language": "english",
  "requires_human": false,
  "requires_human_reason": ""
}

Rules:
1. Confidence must be between 0.0 and 1.0.
2. Sentiment score must be between -1.0 and 1.0.
3. Detect multi-issue messages using all_categories.
4. Hinglish means mixed Hindi and English.
5. Sarcasm such as "great support, waited 3 days" should be Complaint with sarcasm_detected true.
6. Escalation signals include "speak to manager", "legal action", "unacceptable", "very disappointed".
7. Technical Glitch, Complaint, Feature Request, and Escalation usually require a human.
8. Low confidence or multi-issue cases should require a human.
"""


client = Groq(api_key=settings.groq_api_key)


def classify_message(message: str) -> ClassificationResult:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    raw_content = response.choices[0].message.content.strip()
    parsed = json.loads(raw_content)

    return ClassificationResult.model_validate(parsed)
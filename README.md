# WhatsApp Support Automation System

AI-powered support automation backend for WhatsApp-style customer support workflows. The system classifies incoming messages, decides whether they can be auto-resolved, creates and routes human tickets, stores conversation history, sends mock in-app notifications, and captures agent feedback for active learning.

## Assignment Focus

This project is built for an AI Engineer assignment covering:

- Multi-label support message classification
- Confidence scoring and automation thresholds
- Hinglish, sarcasm, frustration, and escalation detection
- Auto-resolution for safe categories
- Human ticket routing for complex cases
- Agent feedback loop for future model improvement
- PostgreSQL-backed support workflow APIs

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Schemas:** Pydantic
- **AI Classifier:** Groq LLM zero-shot classification
- **Testing:** Pytest
- **Notifications:** Mock in-app notification records
- **Realtime:** FastAPI WebSockets

## Why This AI Approach

The MVP uses an LLM-based zero-shot classifier because it performs well on edge cases that are difficult to solve quickly with a small dataset:

- Hinglish and mixed-language messages
- Sarcasm and frustrated tone
- Multi-issue support requests
- Escalation intent
- Structured JSON reasoning

The classifier is isolated in `app/services/ai_classifier.py`, so it can later be replaced with a fine-tuned DistilBERT, BERT, XLM-R, or other custom model trained on `agent_feedback` data.

## Architecture

```text
Customer Message
  -> Chat API
  -> AI Classifier
  -> Decision Engine
  -> Auto Resolver OR Ticket Router
  -> Conversation Store
  -> Notification Store
  -> WebSocket Broadcast
  -> Agent Feedback Loop
  -> Metrics API
```

## Project Structure

```text
whatsapp_api_chat/
  backend/
    app/
      main.py
      config.py
      database.py
      init_db.py
      seed_db.py
      models/
      routers/
      schemas/
      services/
      websocket/
    tests/
    requirements.txt
    .env.example
  dataset/
    sample_conversations.json
  README.md
```

## Core Features

### AI Classification

The classifier returns:

- primary category
- all detected categories
- confidence score
- sentiment score
- sarcasm flag
- frustration level
- escalation flag
- language
- human-review recommendation

Supported categories:

- Attendance Request
- Billing Inquiry
- Account Access
- Technical Glitch
- Complaint
- Feature Request
- General FAQ
- Escalation

### Automation Decision Engine

Auto-resolution only happens when:

- confidence is above threshold
- category is automation-safe
- no sarcasm is detected
- no escalation signal is detected
- frustration is not high/extreme
- message is not multi-issue
- classifier does not request human review

Automatable MVP categories:

- Attendance Request
- Billing Inquiry
- General FAQ

### Ticket Workflow

Human-required cases create tickets that agents can:

- claim
- resolve
- escalate
- submit feedback for

### Feedback Loop

Agent feedback captures:

- suggested category
- actual category
- automation suggested
- automation approved/rejected

This creates labelled data for active learning and future fine-tuning.

### Notifications

The backend creates mock in-app notifications for:

- new assigned tickets
- claimed tickets
- resolved tickets
- escalated tickets

This keeps the notification architecture provider-agnostic. Email, SMS, Twilio, or WhatsApp Cloud API can be added later behind the same concept.

### Realtime Updates

Clients can subscribe to live updates with:

```text
ws://127.0.0.1:8000/ws/{user_id}
```

The chat endpoint broadcasts:

- `chat.processed` to the customer
- `ticket.assigned` to the assigned agent or supervisor

This allows the future customer chat UI and agent dashboard to update without polling.

### Metrics

The metrics endpoint returns:

- ticket counts
- status distribution
- escalation count
- automation rate
- average confidence
- feedback counts
- category breakdown
- agent workload

## Setup

### 1. Create and activate virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 3. Configure environment

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Update values:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/whatsapp_support
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CONFIDENCE_THRESHOLD=0.70
```

### 4. Create PostgreSQL database

Create a database named:

```text
whatsapp_support
```

### 5. Initialize tables

```powershell
cd backend
python -m app.init_db
```

### 6. Seed demo data

```powershell
python -m app.seed_db
```

Expected demo seed:

- 7 users
- 2 invoices

### 7. Run backend

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API Overview

### Health

```http
GET /
GET /health
```

### Users

```http
GET /users/
GET /users/{user_id}
POST /users/
```

### Chat

```http
POST /chat/
```

Example request:

```json
{
  "user_id": "USR-101",
  "message": "Hi, can you mark my attendance for today? Working from home."
}
```

Example response:

```json
{
  "message_id": "generated-conversation-id",
  "classification": {
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
  },
  "decision": "auto_resolve",
  "ticket_id": null,
  "system_response": "Hi Priya Sharma, your attendance has been marked as Present for today. Have a productive day!"
}
```

### Tickets

```http
GET /tickets/
GET /tickets/{ticket_id}
PATCH /tickets/{ticket_id}/claim
PATCH /tickets/{ticket_id}/resolve
PATCH /tickets/{ticket_id}/escalate
PATCH /tickets/{ticket_id}/transfer
POST /tickets/{ticket_id}/feedback
```

### Conversations

```http
GET /conversations/ticket/{ticket_id}
GET /conversations/user/{user_id}
```

### Notifications

```http
GET /notifications/user/{user_id}
PATCH /notifications/{notification_id}
```

### Metrics

```http
GET /metrics/summary
```

### WebSocket

```text
ws://127.0.0.1:8000/ws/{user_id}
```

## Demo Flow

### 1. Auto-resolution

Use `POST /chat/`:

```json
{
  "user_id": "USR-101",
  "message": "Hi, can you mark my attendance for today? Working from home."
}
```

Expected:

- category: Attendance Request
- decision: auto_resolve
- no ticket created
- attendance row updated
- user/system messages stored

### 2. Human ticket creation

Use `POST /chat/`:

```json
{
  "user_id": "USR-312",
  "message": "My payment failed 3 times and now my account is locked. This is ridiculous!"
}
```

Expected:

- multi-issue classification
- human_required decision
- ticket created
- agent notification created

### 3. Escalation

Use `POST /chat/`:

```json
{
  "user_id": "USR-312",
  "message": "I want to speak to a manager. This is unacceptable."
}
```

Expected:

- escalation detected
- supervisor assigned
- high-priority ticket created

### 4. Agent workflow

Use:

```http
PATCH /tickets/{ticket_id}/claim
PATCH /tickets/{ticket_id}/resolve
POST /tickets/{ticket_id}/feedback
```

### 5. Supervisor metrics

Use:

```http
GET /metrics/summary
```

## Dataset

The dataset is available at:

```text
dataset/sample_conversations.json
```

It contains:

- 30 labelled conversations
- all 8 categories
- Hinglish examples
- sarcasm/frustration examples
- escalation examples
- multi-issue examples
- expected action labels
- minimum expected confidence labels

## Tests

Run:

```powershell
cd backend
python -m pytest tests
```

Current tests cover:

- config loading
- decision engine auto-resolution
- sarcasm routing
- multi-issue routing

LLM API calls are intentionally not tested live in unit tests. They should be mocked in CI to avoid flaky tests and API key exposure.

## Production Improvements

Given more time, I would add:

- Alembic migrations
- JWT authentication and role-based access control
- WebSocket live chat updates
- background notification worker
- Redis/Celery task queue
- model evaluation script against the dataset
- Docker Compose for API + PostgreSQL
- frontend agent dashboard
- fine-tuned DistilBERT or XLM-R classifier using feedback data

## Technical Report

LaTeX report source:

```text
docs/technical_report.tex
```

Compile it with any LaTeX distribution to produce the final PDF report.

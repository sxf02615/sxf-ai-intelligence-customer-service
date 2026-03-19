# Python Core - Core Business Layer

The core business layer of the Smart Ticket System, responsible for intent recognition and business logic processing.

## Module Responsibilities

- **Intent Recognition**: Uses LangChain + Pydantic to recognize user intents
- **Logistics Query**: Queries order status and logistics tracking
- **Urgent Service**: Creates tickets and notifies customer service
- **Cancel Service**: Validates order status and processes refunds
- **Data Abstraction Layer**: Unified Repository interface, supports Mock/Real data source switching

## Tech Stack

- FastAPI - Web Framework
- LangChain - AI Framework
- Pydantic - Data Validation
- OpenAI API - LLM Support

## Project Structure

```
python-core/
├── app/
│   ├── api/              # API Routes
│   │   └── routes.py
│   ├── config.py         # Configuration
│   ├── main.py           # Application Entry
│   ├── models/           # Data Models
│   ├── repositories/     # Data Abstraction Layer
│   └── services/         # Business Services
│       ├── intent_recognition.py  # Intent Recognition
│       ├── logistics.py           # Logistics Query
│       ├── urgent.py              # Urgent Service
│       └── cancel.py              # Cancel Service
├── data/
│   └── mock_data.py      # Mock Data
├── tests/                # Tests
├── requirements.txt
└── .env.example
```

## API Endpoints

### Chat Interface
```http
POST /api/v1/chat
Content-Type: application/json

{
  "session_id": "string",
  "user_id": "string",
  "message": "string"
}
```

### Logistics Query
```http
GET /api/v1/logistics/{order_id}
```

### Urgent Ticket
```http
POST /api/v1/tickets/urgent
Content-Type: application/json

{
  "order_id": "string",
  "reason": "string"
}
```

### Cancel Order
```http
POST /api/v1/orders/cancel
Content-Type: application/json

{
  "order_id": "string",
  "reason": "string"
}
```

## Configuration

Create a `.env` file:

```bash
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

## Start Service

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Data Models

### Order
- order_id: Order number (ORD+digits)
- status: Order status (pending/processing/shipped/delivered/cancelled)
- amount: Amount
- created_at: Creation time

### Ticket
- ticket_id: Ticket ID (TKT+timestamp)
- order_id: Related order number
- reason: Urgent/Cancel reason
- priority: Priority (low/medium/high)
- status: Ticket status (open/in_progress/resolved)
- created_at: Creation time
- estimated_processing_time: Estimated processing time

### LogisticsInfo
- order_id: Order number
- status: Order status
- latest_status: Latest logistics status
- estimated_delivery: Estimated delivery time
- tracking_history: Tracking history (last 3)

## Extensibility

- **LLM Replaceable**: Switch different models via `LLM_PROVIDER` configuration
- **Data Source Replaceable**: Implement Repository interface to connect to real business systems
- **Intent Recognition Prompts**: Independently configured, customizable
# Python Core - Smart Ticket System Core Service

English | [简体中文](./README.md)

The core business layer of the Smart Ticket System, implementing natural language dialogue based on Large Language Models (LLM), automatically recognizing user intent and handling logistics queries, urgent tickets, order cancellations, and other business operations.

## ✨ Core Features

- 🤖 **Intelligent Intent Recognition**: Structured output based on LangChain + Pydantic
- 💬 **Multi-turn Dialogue Management**: Smart context management with flexible conversation order
- 🔄 **Automatic Error Recovery**: Maintains intent when order doesn't exist, allows retry
- 🎯 **Flexible Conversation Order**: Supports intent-first or order-ID-first approaches
- 🌐 **Multi-LLM Support**: Supports OpenAI, DeepSeek, Doubao, Qwen, and more
- 🔌 **Data Abstraction Layer**: Repository pattern for easy integration with real business systems

## 📋 Supported Business Scenarios

### 1. Logistics Query
Query order status, tracking history, and estimated delivery time

### 2. Urgent Ticket Service
Create urgent tickets and notify customer service

### 3. Order Cancellation
Validate order status and process refunds

## 🎯 Conversation Examples

### Scenario 1: Intent First, Then Order ID
```
👤 User: I want to expedite my order
🤖 System: Please provide your order number
👤 User: ORD001
🤖 System: Urgent ticket created successfully
```

### Scenario 2: Order ID First, Then Intent
```
👤 User: ORD001
🤖 System: What would you like to do? Check logistics, expedite, or cancel order?
👤 User: Expedite
🤖 System: Urgent ticket created successfully
```

### Scenario 3: Order Not Found Retry
```
👤 User: I want to expedite my order
🤖 System: Please provide your order number
👤 User: ORD999
🤖 System: Order not found, please provide a valid order number
👤 User: ORD001
🤖 System: Urgent ticket created successfully
```

### Scenario 4: Complete Information at Once
```
👤 User: Please expedite order ORD001
🤖 System: Urgent ticket created successfully
```

## 🏗️ Technical Architecture

### Tech Stack

- **FastAPI** - High-performance web framework
- **LangChain** - LLM application development framework
- **Pydantic** - Data validation and structured output
- **Multi-LLM Support** - OpenAI, DeepSeek, Doubao, Qwen, etc.

### Project Structure

```
python-core/
├── app/
│   ├── api/              # API routes
│   │   └── routes.py    # Chat, logistics, urgent, cancel endpoints
│   ├── config.py         # Configuration management
│   ├── main.py           # Application entry point
│   ├── models/           # Data models
│   ├── repositories/     # Data abstraction layer
│   └── services/         # Business services
│       ├── intent_recognition.py  # Intent recognition
│       ├── llm_factory.py        # LLM factory
│       ├── logistics.py          # Logistics query
│       ├── urgent.py             # Urgent ticket service
│       └── cancel.py             # Order cancellation
├── data/
│   └── mock_data.py      # Mock data
├── tests/                # Test files
├── docs/                 # Documentation
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── README.md             # Chinese README
├── README-en.md          # This file
└── DEVELOPER_GUIDE.md    # Developer guide
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the project
git clone <repository-url>
cd python-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file to configure LLM
# At least one LLM provider must be configured
```

**Minimal Configuration Example**:

```bash
# Using OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Or using DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
```

### 3. Start Service

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Access API documentation
# http://localhost:8000/docs
```

### 4. Test API

```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "user_id": "test_user",
    "message": "I want to expedite my order"
  }'

# Test logistics query
curl "http://localhost:8000/api/v1/logistics/ORD001"
```

## 📡 API Endpoints

### Chat Endpoint

**Endpoint**: `POST /api/v1/chat`

**Request Example**:
```json
{
  "session_id": "session_123",
  "user_id": "user_456",
  "message": "I want to expedite my order",
  "context": {
    "pending_order_id": null,
    "pending_intent": null
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "response": "Please provide your order number",
  "intent": "urgent",
  "session_id": "session_123",
  "needs_clarification": true,
  "clarification_question": "Please provide order number",
  "context": {
    "pending_order_id": null,
    "pending_intent": "urgent"
  }
}
```

### Logistics Query Endpoint

**Endpoint**: `GET /api/v1/logistics/{order_id}`

### Urgent Ticket Endpoint

**Endpoint**: `POST /api/v1/tickets/urgent`

### Order Cancellation Endpoint

**Endpoint**: `POST /api/v1/orders/cancel`

For detailed API documentation, visit: `http://localhost:8000/docs`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| LLM_PROVIDER | LLM provider (openai/deepseek/doubao/qwen) | openai |
| OPENAI_API_KEY | OpenAI API Key | - |
| OPENAI_MODEL | OpenAI model | gpt-3.5-turbo |
| DEEPSEEK_API_KEY | DeepSeek API Key | - |
| DEEPSEEK_MODEL | DeepSeek model | deepseek-chat |
| INTENT_CONFIDENCE_THRESHOLD | Intent recognition confidence threshold | 0.7 |
| API_PORT | API service port | 8000 |

### LLM Switching

```bash
# Switch to DeepSeek
export LLM_PROVIDER=deepseek

# Switch to Doubao
export LLM_PROVIDER=doubao

# Switch to Qwen
export LLM_PROVIDER=qwen
```

For detailed LLM configuration, see: [LLM_SWITCHING_GUIDE.md](./LLM_SWITCHING_GUIDE.md)

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python test_all_context_scenarios.py

# Run individual tests
python test_context_optimization.py
python test_order_not_found_retry.py
python test_order_first_intent_second.py
```

### Test Coverage

- ✅ Basic context optimization
- ✅ Order not found retry
- ✅ Order ID first then intent
- ✅ Order ID with different intent
- ✅ Clarification logic handling
- ✅ Comprehensive scenario testing

## 🐳 Docker Deployment

### Using Docker

```bash
# Build image
docker build -t smart-ticket-core .

# Run container
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=your-key \
  --name smart-ticket-core \
  smart-ticket-core
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f python-core
```

## 📚 Documentation

### Core Documentation
- [Developer Guide](./DEVELOPER_GUIDE.md) - Complete development guide
- [Chinese README](./README.md) - Chinese documentation

### Feature Documentation
- [Context Management Summary](./CONTEXT_MANAGEMENT_SUMMARY.md) - Complete context management guide
- [Context Optimization](./CONTEXT_OPTIMIZATION.md) - Context optimization principles
- [Intent Persistence](./INTENT_PERSISTENCE_FIX.md) - Intent persistence fix
- [Order ID Persistence](./ORDER_ID_PERSISTENCE_FIX.md) - Order ID persistence fix
- [Order First Intent Second](./ORDER_FIRST_INTENT_SECOND.md) - Flexible conversation order
- [Clarification Logic](./CLARIFICATION_LOGIC_FIX.md) - Clarification logic optimization

### Other Documentation
- [LLM Switching Guide](./LLM_SWITCHING_GUIDE.md) - Multi-LLM support guide

## 🔧 Development Guide

### Adding New Intent Types

1. Define new intent type in `app/models/__init__.py`
2. Update prompts in `app/services/intent_recognition.py`
3. Implement corresponding business service
4. Add route handling in `app/api/routes.py`

For detailed steps, see: [Developer Guide](./DEVELOPER_GUIDE.md)

### Custom Data Source

Implement the `Repository` interface to integrate with real business systems:

```python
from app.repositories.base import OrderRepository

class MySQLOrderRepository(OrderRepository):
    def get_by_id(self, order_id: str) -> Optional[Order]:
        # Implement MySQL query
        pass
```

## 🐛 Troubleshooting

### Common Issues

1. **LLM API Call Failure**
   - Check if API Key is correct
   - Check network connection
   - Review error messages in logs

2. **Context Loss**
   - Check if frontend correctly passes `context` parameter
   - Verify `session_id` consistency

3. **Inaccurate Intent Recognition**
   - Adjust confidence threshold
   - Optimize intent recognition prompts

For detailed troubleshooting, see: [Developer Guide - Troubleshooting](./DEVELOPER_GUIDE.md#故障排查)

## 📈 Performance Optimization

- ✅ Smart context management reduces 30-50% LLM calls
- ✅ Asynchronous processing improves response speed
- ✅ Structured output improves accuracy
- ✅ Repository pattern supports data caching

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Contact

For questions or suggestions:
- Submit an Issue
- Check the [Developer Guide](./DEVELOPER_GUIDE.md)
- Read related documentation

---

**Last Updated**: 2024-01-15

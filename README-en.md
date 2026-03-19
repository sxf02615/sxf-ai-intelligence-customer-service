# Smart Ticket System

An intelligent customer service ticket system based on LangChain.

## Overview

This system is an intelligent customer service ticket system built on LangChain, supporting three core features:
- **Order Logistics Query** - Users can input order numbers to query real-time logistics status
- **Urgent Order Processing** - Users can request order acceleration, and the system creates tickets to notify customer service
- **Order Cancellation** - Users can cancel orders, and the system validates and processes refunds

## System Architecture

The system uses a three-tier architecture:

```
┌─────────────────────────────────────────┐
│         UI Layer (Python FastAPI)       │
│         python-ui (Port 8001)           │
└─────────────────┬───────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────┐
│      User Layer (Java Spring Boot)      │
│         java-service (Port 8080)        │
└─────────────────┬───────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────┐
│    Core Business Layer (Python)         │
│        python-core (Port 8000)          │
└─────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI Layer | Python FastAPI + HTML + JavaScript |
| User Layer | Java Spring Boot 3.x |
| Core Business Layer | Python 3.9+ + FastAPI + LangChain |
| AI Framework | LangChain + OpenAI API |
| Data Validation | Pydantic |

## Core Features

### 1. Intent Recognition
- Uses LangChain + Pydantic for structured output
- Recognizes three intents: logistics, urgent, cancel
- Extracts order number entities (format: ORD+digits)
- Returns clarification questions when confidence is below 0.7

### 2. Logistics Query
- Query order status by order number
- Query logistics tracking for shipped orders
- Returns formatted logistics info (latest status, estimated delivery, last 3 tracking events)

### 3. Urgent Order Processing
- Multi-turn conversation to collect order number and reason (optional)
- Creates and saves tickets
- Notifies customer service (via log simulation)
- Returns ticket ID, estimated processing time, and contact info

### 4. Order Cancellation
- Multi-turn conversation to collect order number and reason
- Validates order status (cancelled/delivered/other)
- Processes refund and returns results

## Quick Start

### Prerequisites

- Python 3.9+
- Java 17+
- Docker & Docker Compose (optional)

### Start with Docker Compose

```bash
docker-compose up -d
```

After startup:
- UI: http://localhost:8001
- Java Service: http://localhost:8080
- Python Core Service: http://localhost:8000

### Manual Startup

1. **Start Python Core Service**
```bash
cd python-core
pip install -r requirements.txt
cp .env.example .env
# Edit .env to configure OpenAI API Key
uvicorn app.main:app --reload --port 8000
```

2. **Start Java Service**
```bash
cd java-service
mvn spring-boot:run
```

3. **Start Python UI**
```bash
cd python-ui
pip install -r requirements.txt
cp .env.example .env
# Edit .env to configure Java service URL
uvicorn app.main:app --reload --port 8001
```

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| user | user123 | User |

## Test Order Numbers

- ORD001 - Shipped
- ORD002 - Delivered
- ORD003 - Cancelled

## Project Structure

```
smart-ticket-system/
├── python-core/          # Core business layer
├── java-service/         # User layer
├── python-ui/            # UI layer
├── docker-compose.yml    # Container orchestration
└── README.md
```

## Module Documentation

- [python-core Module](./python-core/README.md)
- [java-service Module](./java-service/README.md)
- [python-ui Module](./python-ui/README.md)
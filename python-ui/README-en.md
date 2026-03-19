# Python UI - User Interface Layer

The UI layer of the Smart Ticket System, providing login and chat interfaces.

## Module Responsibilities

- **Login Page**: User authentication entry
- **Chat Interface**: Intelligent customer service interaction interface
- **API Proxy**: Forwards requests to Java User Layer

## Tech Stack

- FastAPI - Web Framework
- Jinja2 - Template Engine
- httpx - Async HTTP Client

## Project Structure

```
python-ui/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application Entry
│   ├── config.py         # Configuration
│   ├── api/              # API Routes
│   │   ├── auth.py       # Authentication
│   │   └── chat.py       # Chat
│   ├── services/
│   │   └── http_client.py # HTTP Client
│   ├── templates/        # HTML Templates
│   │   ├── login.html
│   │   └── chat.html
│   └── static/           # Static Resources
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── requirements.txt
└── .env.example
```

## Page Description

### Login Page (login.html)
- Username/Password input
- Login button
- Error message display

### Chat Page (chat.html)
- Message display area
- Message input field
- Send button
- Intent recognition result display
- Loading state indicator

## Configuration

Create a `.env` file:

```bash
JAVA_SERVICE_URL=http://localhost:8080
SESSION_SECRET=your-secret-key
```

## Start Service

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

Access http://localhost:8001 after startup

## Frontend Interaction Flow

1. User visits login page
2. Enter username/password, click login
3. UI calls Java authentication service
4. On success, redirect to chat page
5. User sends message
6. UI calls Java chat service
7. Java forwards to Python Core for processing
8. Return result and display

## Static Resources

- `static/css/style.css` - Page styles
- `static/js/app.js` - Frontend interaction logic

## Extensibility

- **UI Replaceable**: FastAPI provides REST API, can be replaced with other frontend frameworks
- **Theme Customization**: CSS files can be customized
- **Feature Extension**: Can add more pages and features
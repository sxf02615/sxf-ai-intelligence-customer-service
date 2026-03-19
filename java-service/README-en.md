# Java Service - User Layer

The user layer of the Smart Ticket System, responsible for authentication, session management, and request forwarding.

## Module Responsibilities

- **Authentication Service**: User login authentication, Token management
- **Session Management**: User session maintenance
- **Request Forwarding**: Forwards requests to Python Core Business Layer
- **API Gateway**: Unified entry, load balancing (reserved)

## Tech Stack

- Spring Boot 3.x
- Spring Cloud OpenFeign - HTTP Client
- Maven - Build Tool

## Project Structure

```
java-service/
├── src/main/java/com/smartticket/
│   ├── SmartTicketApplication.java  # Application Entry
│   ├── config/                      # Configuration Classes
│   │   ├── WebConfig.java
│   │   ├── FeignConfig.java
│   │   └── SecurityConfig.java
│   ├── controller/                  # Controllers
│   │   ├── AuthController.java      # Authentication
│   │   ├── ChatController.java      # Chat
│   │   └── HealthController.java    # Health Check
│   ├── dto/                         # Data Transfer Objects
│   │   ├── LoginRequest.java
│   │   ├── LoginResponse.java
│   │   ├── ChatRequest.java
│   │   ├── ChatResponse.java
│   │   └── ApiResponse.java
│   ├── service/                     # Service Layer
│   │   ├── AuthService.java         # Auth Service Interface
│   │   ├── ChatService.java         # Chat Service
│   │   └── impl/
│   │       └── AuthServiceImpl.java # Auth Service Implementation
│   ├── feign/                       # Feign Client
│   │   └── TicketServiceClient.java
│   └── repository/                  # Data Repository
│       ├── AuthRepository.java      # Auth Repository Interface
│       └── ConfigAuthRepository.java # Config Auth Implementation
├── src/main/resources/
│   ├── application.yml
│   └── application-dev.yml
└── pom.xml
```

## API Endpoints

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

# Response
{
  "success": true,
  "data": {
    "token": "string",
    "user_id": "string",
    "expires_in": 3600
  }
}
```

### Chat
```http
POST /api/v1/chat
Content-Type: application/json
Authorization: Bearer {token}

{
  "session_id": "string",
  "user_id": "string",
  "message": "string"
}
```

### Health Check
```http
GET /health
```

## Configuration

### application.yml
```yaml
server:
  port: 8080

python-core:
  url: http://localhost:8000

spring:
  application:
    name: smart-ticket-service
```

### Auth Users Configuration (application-dev.yml)
```yaml
app:
  auth:
    users:
      - username: admin
        password: admin123
        role: admin
      - username: user
        password: user123
        role: user
    auth-mode: config
```

## Start Service

```bash
mvn spring-boot:run
```

Access http://localhost:8080 after startup

## Authentication Service Design

### Abstract Interface
```java
public interface AuthService {
    AuthResult authenticate(String username, String password);
    UserInfo getUserByToken(String token);
    boolean validateToken(String token);
    void logout(String token);
}
```

### Auth Modes
- **config mode**: Reads user info from configuration file (current)
- **business mode**: Connects to business system authentication (reserved)

## Extensibility

- **Authentication Extensible**: Implement AuthRepository interface to connect to business systems
- **Microservices Transformation**: Reserved API Gateway and service registration/discovery interfaces
- **Load Balancing**: Supports multiple Python Core service instances
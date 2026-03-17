# Implementation Plan: Smart Ticket System

## Overview

This implementation plan outlines the development of a smart ticket system using a three-tier architecture:
- **python-core**: Core business logic with intent recognition, logistics, urgent ticket, and cancel order services
- **java-service**: User layer for authentication, session management, and API gateway
- **python-ui**: FastAPI-based user interface with login and chat pages

The implementation follows a bottom-up approach, starting with the data layer and core services, then building up to the user layer and UI.

## Tasks

### 1. Python Core - Data Layer Setup

- [x] 1.1 Create project structure for python-core
  - Create directory structure: app/, data/, tests/
  - Set up __init__.py files
  - Create requirements.txt with dependencies (fastapi, langchain, pydantic, uvicorn)
  - Create .env.example for configuration
  - _Requirements: NFR3, NFR4, NFR5_

- [x] 1.2 Define core data models
  - Create app/models/__init__.py
  - Implement Order model (order_id, status, amount, created_at)
  - Implement LogisticsInfo model (order_id, status, latest_status, estimated_delivery, tracking_history)
  - Implement Ticket model (ticket_id, order_id, reason, priority, status, created_at, estimated_processing_time)
  - Implement Intent models (IntentType, IntentResult, IntentEntities)
  - _Requirements: DR4, DR5, DR6_

- [x] 1.3 Implement data abstraction layer
  - Create app/repositories/__init__.py
  - Define OrderRepository abstract interface (get_by_id, update_status, cancel)
  - Define LogisticsRepository abstract interface (get_tracking, get_estimated_delivery)
  - Define TicketRepository abstract interface (create, get_by_id, list_by_order)
  - _Requirements: DR1, DR2, DR3_

- [x] 1.4 Implement mock data sources
  - Create data/mock_data.py
  - Implement MockOrderRepository with test data (ORD001-shipped, ORD002-delivered, ORD003-cancelled)
  - Implement MockLogisticsRepository with tracking events
  - Implement MockTicketRepository for ticket storage
  - _Requirements: DR4, DR5, DR6_

- [x] 1.5 Set up configuration management
  - Create app/config.py
  - Define configuration settings using Pydantic Settings
  - Configure LLM settings (OpenAI API key, model name)
  - Configure repository settings (mock vs real data source)
  - _Requirements: NFR4, NFR5_

- [x] 1.6 Write property tests for data models
  - **Property 1**: Order status validation
  - **Validates: Requirements DR4**
  - **Property 2**: Ticket ID format validation (TKT+timestamp)
  - **Validates: Requirements DR6**
  - **Property 3**: Mock data round-trip consistency
  - **Validates: Requirements DR2, DR3**

### 2. Python Core - Core Services Implementation

- [x] 2.1 Implement Intent Recognition Service
  - Create app/services/intent_recognition.py
  - Implement LangChain integration with structured output
  - Create prompt template for intent classification
  - Implement confidence threshold check (0.7)
  - Handle clarification when confidence is low
  - _Requirements: FR2.1, FR2.2, FR2.3, FR2.4, FR2.5_

- [x] 2.2 Implement Logistics Service
  - Create app/services/logistics.py
  - Implement order status retrieval
  - Implement tracking history retrieval (last 3 events)
  - Implement estimated delivery time calculation
  - Format response with latest_status, estimated_delivery, tracking_history
  - _Requirements: FR3.1, FR3.2, FR3.3, FR3.4_

- [x] 2.3 Implement Urgent Ticket Service
  - Create app/services/urgent.py
  - Implement ticket creation with TKT+timestamp ID generation
  - Implement priority assignment logic
  - Implement estimated processing time calculation
  - Implement客服 notification (logging)
  - _Requirements: FR4.1, FR4.2, FR4.3, FR4.4_

- [x] 2.4 Implement Cancel Order Service
  - Create app/services/cancel.py
  - Implement order status validation (cancelled, delivered, other)
  - Implement cancel logic for valid orders
  - Implement refund amount calculation
  - Implement refund arrival time calculation
  - _Requirements: FR5.1, FR5.2, FR5.3, FR5.4, FR5.5_

- [ ]* 2.5 Write property tests for core services
  - **Property 4**: Intent recognition round-trip (parse → print → parse)
  - **Validates: Requirements FR2.1**
  - **Property 5**: Logistics info completeness
  - **Validates: Requirements FR3.4**
  - **Property 6**: Ticket creation idempotence
  - **Validates: Requirements FR4.2**
  - **Property 7**: Cancel order state machine
  - **Validates: Requirements FR5.2, FR5.3**

### 3. Python Core - API Routes

- [ ] 3.1 Create API router structure
  - Create app/api/__init__.py
  - Create app/api/routes.py
  - Set up FastAPI application instance
  - Configure CORS for cross-origin requests
  - _Requirements: NFR1_

- [ ] 3.2 Implement chat API endpoint
  - POST /api/v1/chat
  - Implement intent recognition routing
  - Route to appropriate service (logistics, urgent, cancel)
  - Return structured response with intent, response, session_id
  - _Requirements: FR2.2, FR2.3, FR2.4_

- [ ] 3.3 Implement logistics API endpoint
  - GET /api/v1/logistics/{order_id}
  - Validate order_id format (ORD+数字)
  - Return formatted logistics information
  - Handle order not found error
  - _Requirements: FR3.1, FR3.2, FR3.3, FR3.4_

- [ ] 3.4 Implement urgent ticket API endpoint
  - POST /api/v1/tickets/urgent
  - Accept order_id and optional reason
  - Create ticket and return ticket_id, estimated_processing_time, contact
  - _Requirements: FR4.1, FR4.2, FR4.3, FR4.4_

- [ ] 3.5 Implement cancel order API endpoint
  - POST /api/v1/orders/cancel
  - Accept order_id and reason
  - Validate order status and process cancellation
  - Return cancel result with refund information
  - _Requirements: FR5.1, FR5.2, FR5.3, FR5.4, FR5.5_

- [ ] 3.6 Create main application entry point
  - Create app/main.py
  - Import and include API routes
  - Add health check endpoint
  - Configure startup events
  - _Requirements: NFR1, NFR3_

- [ ]* 3.7 Write property tests for API endpoints
  - **Property 8**: API response format consistency
  - **Validates: Requirements NFR1**
  - **Property 9**: Order ID format validation
  - **Validates: Requirements FR2.3**

### 4. Java Service - Project Setup and Configuration

- [ ] 4.1 Create Java project structure
  - Create java-service directory with Maven structure
  - Set up pom.xml with Spring Boot 3.x dependencies
  - Create src/main/java/com/smartticket/ package structure
  - Create src/main/resources/ directory
  - _Requirements: NFR2_

- [ ] 4.2 Configure application settings
  - Create application.yml with server port configuration
  - Configure Python core service URL
  - Set up application-dev.yml for development profile
  - _Requirements: NFR2, NFR8_

- [ ] 4.3 Create DTO classes
  - Create dto/LoginRequest.java (username, password)
  - Create dto/LoginResponse.java (success, token, user_id, expires_in)
  - Create dto/ChatRequest.java (session_id, user_id, message, context)
  - Create dto/ChatResponse.java (success, response, intent, session_id, needs_clarification)
  - Create dto/ApiResponse.java for consistent API response format
  - _Requirements: FR1.2, FR1.3_

### 5. Java Service - Authentication Module

- [ ] 5.1 Implement authentication abstraction
  - Create service/AuthService.java interface
  - Define authenticate(username, password) method
  - Define getUserByToken(token) method
  - Define validateToken(token) method
  - Define logout(token) method
  - _Requirements: FR1.5, FR1.6_

- [ ] 5.2 Implement configuration-based authentication
  - Create repository/AuthRepository.java abstract interface
  - Create repository/ConfigAuthRepository.java for file-based auth
  - Implement user validation against configuration
  - Support multiple users (admin, user roles)
  - _Requirements: FR1.1, FR1.2, FR1.4, FR1.6_

- [ ] 5.3 Implement AuthService implementation
  - Create service/impl/AuthServiceImpl.java
  - Integrate AuthRepository for user lookup
  - Implement token generation (simple JWT or UUID)
  - Implement token validation logic
  - _Requirements: FR1.3, FR1.5_

- [ ] 5.4 Create authentication controller
  - Create controller/AuthController.java
  - POST /api/v1/auth/login endpoint
  - Validate login credentials
  - Return token on success
  - Return error message on failure
  - _Requirements: FR1.1, FR1.2, FR1.3_

- [ ]* 5.5 Write unit tests for authentication
  - Test successful login with valid credentials
  - Test failed login with invalid credentials
  - Test token validation
  - Test logout functionality
  - _Requirements: FR1.1, FR1.2, FR1.3_

### 6. Java Service - Chat and Integration

- [ ] 6.1 Implement Python core service client
  - Create feign/TicketServiceClient.java (Feign client)
  - Configure base URL from configuration
  - Implement chat() method (POST /api/v1/chat)
  - Implement getLogistics(orderId) method (GET /api/v1/logistics/{orderId})
  - Implement createUrgentTicket(request) method (POST /api/v1/tickets/urgent)
  - Implement cancelOrder(request) method (POST /api/v1/orders/cancel)
  - _Requirements: NFR7, NFR8_

- [ ] 6.2 Implement chat service
  - Create service/ChatService.java
  - Integrate TicketServiceClient for Python core calls
  - Handle response mapping
  - Implement error handling
  - _Requirements: NFR7, NFR8_

- [ ] 6.3 Create chat controller
  - Create controller/ChatController.java
  - POST /api/v1/chat endpoint
  - Validate request (session_id, user_id, message)
  - Call ChatService and return response
  - _Requirements: NFR7_

- [ ] 6.4 Create health check controller
  - Create controller/HealthController.java
  - GET /health endpoint
  - Return service status
  - _Requirements: NFR2_

- [ ] 6.5 Configure Spring Boot application
  - Create SmartTicketApplication.java main class
  - Create config/WebConfig.java for web configuration
  - Create config/FeignConfig.java for Feign client
  - _Requirements: NFR2_

- [ ]* 6.6 Write integration tests for Java service
  - Test authentication flow end-to-end
  - Test chat routing to Python core
  - Test error handling and response mapping
  - _Requirements: NFR7, NFR8_

### 7. Python UI - Project Setup

- [ ] 7.1 Create Python UI project structure
  - Create python-ui directory
  - Set up app/ directory structure (api/, templates/, static/, services/)
  - Create requirements.txt with dependencies (fastapi, httpx, jinja2)
  - Create .env.example for configuration
  - _Requirements: NFR1_

- [ ] 7.2 Configure UI settings
  - Create app/config.py
  - Configure Java service URL
  - Configure session settings
  - Configure static file paths
  - _Requirements: NFR1, NFR7_

### 8. Python UI - Login Page Implementation

- [ ] 8.1 Create login HTML template
  - Create templates/login.html
  - Design login form (username, password fields)
  - Add submit button
  - Add error message display area
  - Style with CSS for clean, user-friendly appearance
  - _Requirements: FR1.1_

- [ ] 8.2 Implement login API endpoint
  - Create app/api/auth.py
  - POST /api/auth/login endpoint
  - Call Java authentication service
  - Handle success/failure responses
  - Set session/token on successful login
  - _Requirements: FR1.1, FR1.2, FR1.3_

- [ ] 8.3 Implement login page route
  - GET /login endpoint
  - Render login.html template
  - Handle already logged-in users (redirect to chat)
  - _Requirements: FR1.1_

- [ ] 8.4 Create HTTP client for Java service
  - Create services/http_client.py
  - Implement async HTTP client using httpx
  - Handle authentication token in requests
  - Implement error handling and retry logic
  - _Requirements: NFR7_

- [ ]* 8.5 Write unit tests for login functionality
  - Test login page rendering
  - Test successful authentication flow
  - Test failed authentication handling
  - Test session management
  - _Requirements: FR1.1, FR1.2, FR1.3_

### 9. Python UI - Chat Page Implementation

- [ ] 9.1 Create chat HTML template
  - Create templates/chat.html
  - Design chat interface (message display area, input field, send button)
  - Add loading indicator
  - Add error message display
  - Style with CSS for comfortable chat experience
  - _Requirements: FR2.1, FR2.2, FR2.3, FR2.4_

- [ ] 9.2 Implement chat API endpoint
  - Create app/api/chat.py
  - POST /api/chat endpoint
  - Call Java chat service
  - Return response with intent information
  - _Requirements: NFR7_

- [ ] 9.3 Implement chat page route
  - GET /chat endpoint
  - Check authentication (redirect to login if not authenticated)
  - Render chat.html template
  - _Requirements: FR1.5_

- [ ] 9.4 Implement chat JavaScript functionality
  - Create static/js/app.js
  - Implement message sending via WebSocket or polling
  - Implement message display and formatting
  - Handle intent-specific response formatting (logistics, urgent, cancel)
  - Implement loading states
  - _Requirements: FR2.1, FR2.2, FR2.3, FR2.4_

- [ ] 9.5 Implement logout functionality
  - POST /api/auth/logout endpoint
  - Clear session/token
  - Redirect to login page
  - _Requirements: FR1.5_

- [ ]* 9.6 Write unit tests for chat functionality
  - Test chat page rendering
  - Test message sending and receiving
  - Test intent-specific response handling
  - Test error handling
  - _Requirements: FR2.1, FR2.2, FR2.3, FR2.4_

### 10. Integration and Testing

- [ ] 10.1 Create Docker Compose configuration
  - Create docker-compose.yml
  - Define python-core service (port 8000)
  - Define java-service service (port 8080)
  - Define python-ui service (port 8001)
  - Configure network between services
  - _Requirements: NFR7, NFR8_

- [ ] 10.2 Integration testing - Authentication flow
  - Test login from UI to Java auth service
  - Test token propagation to Python core
  - Test session validation
  - _Requirements: FR1.1, FR1.2, FR1.3_

- [ ] 10.3 Integration testing - Chat flow
  - Test message from UI to Java to Python core
  - Test intent recognition routing
  - Test response formatting and display
  - _Requirements: FR2.1, FR2.2, FR2.3, FR2.4, FR2.5_

- [ ] 10.4 Integration testing - Business logic
  - Test logistics query flow end-to-end
  - Test urgent ticket creation flow end-to-end
  - Test cancel order flow end-to-end
  - _Requirements: FR3.1, FR3.2, FR3.3, FR3.4, FR4.1, FR4.2, FR4.3, FR4.4, FR5.1, FR5.2, FR5.3, FR5.4, FR5.5_

- [ ] 10.5 Final checkpoint - System validation
  - Run all unit tests
  - Run all property-based tests
  - Run all integration tests
  - Verify all acceptance criteria are met
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end functionality
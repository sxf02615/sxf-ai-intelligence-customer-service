# 智能工单系统设计文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        UI Layer (Python)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI + HTML/Thymeleaf                    │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │   │
│  │  │  Login    │ │  Chat     │ │  Dashboard│             │   │
│  │  │  Page     │ │  Interface│ │  Page     │             │   │
│  │  └───────────┘ └───────────┘ └───────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        User Layer (Java)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Spring Boot - API Gateway / User Service      │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐               │   │
│  │  │  REST     │ │  Auth     │ │  Session  │               │   │
│  │  │  API      │ │  Service  │ │  Manager  │               │   │
│  │  └───────────┘ └───────────┘ └───────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Business Layer (Python)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI - Core Business Service             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │   │
│  │  │  Intent     │ │  Session    │ │  Response   │       │   │
│  │  │  Router     │ │  Manager    │ │  Generator  │       │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services (Python)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  Logistics  │ │  Urgent     │ │  Cancel     │               │
│  │  Service    │ │  Service    │ │  Service    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Abstraction Layer (Python)               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  Order      │ │  Logistics  │ │  Ticket     │               │
│  │  Repository │ │  Repository │ │  Repository │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Sources                                │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  Mock Data Source   │  │  (预留)              │              │
│  │  (初期实现)          │  │  Real Business      │              │
│  │                     │  │  System Interface   │              │
│  └─────────────────────┘  └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.1 分层职责

| 层级 | 技术栈 | 职责 |
|------|--------|------|
| UI Layer | Python FastAPI + HTML | 用户界面、登录、聊天交互 |
| User Layer | Java Spring Boot | 用户接入、认证、会话管理 |
| Core Business Layer | Python FastAPI | 意图识别、会话管理、响应生成 |
| Core Services | Python | 物流查询、催单、退单业务逻辑 |
| Data Layer | Python | 数据抽象、Mock/真实数据源切换 |

## 2. 模块设计

### 2.1 意图识别模块 (Intent Recognition)

```python
# 意图识别流程
User Input → LLM + Pydantic → Structured Output → Intent + Entities → Confidence Check
                                      │
                                      ▼
                              Confidence >= 0.7 → Route to Service
                              Confidence < 0.7 → Clarification Question
```

**Pydantic Models:**
```python
class IntentType(str, Enum):
    LOGISTICS = "logistics"
    URGENT = "urgent"
    CANCEL = "cancel"

class IntentResult(BaseModel):
    intent: IntentType
    confidence: float
    entities: IntentEntities
    needs_clarification: bool = False
    clarification_question: Optional[str] = None

class IntentEntities(BaseModel):
    order_id: Optional[str] = None  # 格式: ORD+数字
    user_detail: Optional[str] = None
```

### 2.2 物流查询模块 (Logistics Service)

```python
# 物流查询流程
Query → Get Order Status → If Shipped → Get Tracking Info → Format Response
              │
              ▼
        Order Not Found / Invalid → Error Message
```

**Response Model:**
```python
class LogisticsInfo(BaseModel):
    order_id: str
    status: str  # pending, processing, shipped, delivered, cancelled
    latest_status: str
    estimated_delivery: Optional[datetime]
    tracking_history: List[TrackingEvent]  # 最近3条
```

### 2.3 催单模块 (Urgent Service)

```python
# 催单流程
Collect Info → Create Ticket → Save to Storage → Notify (Log) → Return Ticket Info
    │
    ▼
Missing Info → Clarification Question
```

**Ticket Model:**
```python
class Ticket(BaseModel):
    ticket_id: str  # 格式: TKT+时间戳
    order_id: str
    reason: Optional[str]
    priority: str  # low, medium, high
    status: str  # open, in_progress, resolved
    created_at: datetime
    estimated处理_time: datetime
```

### 2.4 退单模块 (Cancel Service)

```python
# 退单流程
Collect Info → Validate Order Status
    │
    ├── Cancelled → Reject: "订单已取消"
    ├── Delivered → Reject: "请走售后退货流程"
    └── Other → Process Cancel → Update Order → Trigger Refund → Return Result
```

**Cancel Result Model:**
```python
class CancelResult(BaseModel):
    success: bool
    order_id: str
    refund_amount: float
    refund_arrival_time: datetime
    message: str
```

## 3. 数据抽象层设计

### 3.1 抽象接口定义

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool:
        pass
    
    @abstractmethod
    def cancel(self, order_id: str, reason: str) -> CancelResult:
        pass

class LogisticsRepository(ABC):
    @abstractmethod
    def get_tracking(self, order_id: str) -> List[TrackingEvent]:
        pass
    
    @abstractmethod
    def get_estimated_delivery(self, order_id: str) -> Optional[datetime]:
        pass

class TicketRepository(ABC):
    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        pass
    
    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        pass
    
    @abstractmethod
    def list_by_order(self, order_id: str) -> List[Ticket]:
        pass
```

### 3.2 Mock 数据源实现

```python
class MockOrderRepository(OrderRepository):
    """模拟订单数据源"""
    
    def __init__(self):
        self.orders = {
            "ORD001": Order(
                order_id="ORD001",
                status="shipped",
                amount=199.00,
                created_at=datetime.now() - timedelta(days=3)
            ),
            "ORD002": Order(
                order_id="ORD002",
                status="delivered",
                amount=299.00,
                created_at=datetime.now() - timedelta(days=7)
            ),
            "ORD003": Order(
                order_id="ORD003",
                status="cancelled",
                amount=99.00,
                created_at=datetime.now() - timedelta(days=2)
            ),
            # ... 更多测试数据
        }
```

## 4. 技术选型

### 4.1 Java 用户层
| 组件 | 选择 | 理由 |
|------|------|------|
| 框架 | Spring Boot 3.x | 企业级、成熟生态、单机部署 |
| 通信 | RestTemplate / WebClient | HTTP 客户端 |
| 配置 | Spring Boot Config | 配置文件管理 |
| 监控 | Spring Actuator | 健康检查、指标监控 |

### 4.2 Python 核心层
| 组件 | 选择 | 理由 |
|------|------|------|
| 后端框架 | FastAPI | 高性能、自动文档、类型安全 |
| AI 框架 | LangChain | 模块化、支持多种 LLM |
| LLM | OpenAI GPT-3.5/4 | 成熟、稳定、支持结构化输出 |
| 数据验证 | Pydantic | 类型安全、自动验证 |
| 配置管理 | Pydantic Settings | 类型安全、环境变量支持 |

## 4.3 认证接口设计

### 4.3.1 认证流程

```
用户 → UI (FastAPI): 登录页面
UI → User Layer (Java): POST /api/v1/auth/login
User Layer → Auth Service: 验证账号密码
Auth Service → Config/User System: 获取用户信息
Auth Service → UI: 返回 Token/Session
UI → 用户: 登录成功，进入聊天界面
```

### 4.3.2 登录接口

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "success": true,
  "data": {
    "token": "string",
    "user_id": "string",
    "expires_in": 3600
  }
}
```

### 4.3.3 认证抽象接口

```java
// 认证服务抽象接口（便于后期对接业务系统）
public interface AuthService {
    
    // 验证用户凭证
    AuthResult authenticate(String username, String password);
    
    // 根据 Token 获取用户信息
    UserInfo getUserByToken(String token);
    
    // 验证 Token 有效性
    boolean validateToken(String token);
    
    // 登出
    void logout(String token);
}

// 认证结果
public class AuthResult {
    private boolean success;
    private String token;
    private String userId;
    private String message;
}
```

### 4.3.4 配置文件中的账号密码

```yaml
# Java 端配置
app:
  auth:
    # 模拟用户账号（后期替换为业务系统对接）
    users:
      - username: "admin"
        password: "admin123"
        role: "admin"
      - username: "user"
        password: "user123"
        role: "user"
    
  # 认证模式：config/file 或 business/system
  auth-mode: config
  
  # 业务系统对接配置（预留）
  business-system:
    enabled: false
    api-url: "http://business-system/api"
    auth-endpoint: "/auth/verify"
```

## 4.4 Java-Python API 协议

### 对话接口
```http
POST /api/v1/chat
Content-Type: application/json

{
  "session_id": "string",
  "user_id": "string",
  "message": "string",
  "context": {}  // 可选的上下文信息
}

Response:
{
  "success": true,
  "data": {
    "response": "string",
    "intent": "logistics|urgent|cancel",
    "session_id": "string",
    "needs_clarification": false
  }
}
```

### 物流查询接口
```http
GET /api/v1/logistics/{order_id}

Response:
{
  "success": true,
  "data": {
    "order_id": "string",
    "status": "string",
    "latest_status": "string",
    "estimated_delivery": "datetime",
    "tracking_history": [...]
  }
}
```

### 催单接口
```http
POST /api/v1/tickets/urgent
Content-Type: application/json

{
  "order_id": "string",
  "reason": "string"
}

Response:
{
  "success": true,
  "data": {
    "ticket_id": "string",
    "estimated处理_time": "datetime",
    "contact": "string"
  }
}
```

### 退单接口
```http
POST /api/v1/orders/cancel
Content-Type: application/json

{
  "order_id": "string",
  "reason": "string"
}

Response:
{
  "success": true,
  "data": {
    "order_id": "string",
    "refund_amount": 0.00,
    "refund_arrival_time": "datetime",
    "message": "string"
  }
}
```

## 4.4 Java Spring Boot 用户层设计

### 4.4.1 模块职责

```java
// 核心类设计
@SpringBootApplication
public class SmartTicketApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmartTicketApplication.class, args);
    }
}

// 对话控制器
@RestController
@RequestMapping("/api/v1")
public class ChatController {
    
    @Autowired
    private ChatService chatService;
    
    @PostMapping("/chat")
    public ApiResponse<ChatResponse> chat(@RequestBody ChatRequest request) {
        return ApiResponse.success(chatService.processMessage(request));
    }
}

// HTTP 客户端 - 调用 Python 核心服务
@Component
public class TicketServiceClient {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Value("${python-core.url}")
    private String pythonCoreUrl;
    
    public CoreResponse chat(ChatRequest request) {
        return restTemplate.postForObject(pythonCoreUrl + "/api/v1/chat", request, CoreResponse.class);
    }
    
    public CoreResponse getLogistics(String orderId) {
        return restTemplate.getForObject(pythonCoreUrl + "/api/v1/logistics/" + orderId, CoreResponse.class);
    }
    
    public CoreResponse createUrgentTicket(UrgentRequest request) {
        return restTemplate.postForObject(pythonCoreUrl + "/api/v1/tickets/urgent", request, CoreResponse.class);
    }
    
    public CoreResponse cancelOrder(CancelRequest request) {
        return restTemplate.postForObject(pythonCoreUrl + "/api/v1/orders/cancel", request, CoreResponse.class);
    }
}
```

### 4.4.2 配置文件

```yaml
# application.yml
server:
  port: 8080

python-core:
  url: http://localhost:8000

spring:
  application:
    name: smart-ticket-service
```

## 6. 项目结构

```
smart_ticket_system/
├── python-ui/                       # Python FastAPI UI 层
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── config.py                # 配置管理
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # 认证接口（调用 Java 后端）
│   │   │   └── chat.py              # 聊天接口（调用 Java 后端）
│   │   ├── templates/
│   │   │   ├── login.html           # 登录页面
│   │   │   └── chat.html            # 聊天页面
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── style.css
│   │   │   └── js/
│   │   │       └── app.js
│   │   └── services/
│   │       ├── __init__.py
│   │       └── http_client.py       # HTTP 客户端（调用 Java 后端）
│   ├── requirements.txt
│   └── .env.example
│
├── java-service/                    # Java Spring Boot 用户层
│   ├── src/main/java/com/smartticket/
│   │   ├── SmartTicketApplication.java
│   │   ├── config/
│   │   │   ├── WebConfig.java        # Web 配置
│   │   │   ├── FeignConfig.java      # Feign 客户端配置
│   │   │   └── SecurityConfig.java   # 安全配置
│   │   ├── controller/
│   │   │   ├── AuthController.java   # 认证接口
│   │   │   ├── ChatController.java   # 对话接口
│   │   │   └── HealthController.java # 健康检查
│   │   ├── dto/
│   │   │   ├── LoginRequest.java
│   │   │   ├── LoginResponse.java
│   │   │   ├── ChatRequest.java
│   │   │   ├── ChatResponse.java
│   │   │   └── ApiResponse.java
│   │   ├── service/
│   │   │   ├── AuthService.java      # 认证服务
│   │   │   ├── ChatService.java      # 对话服务
│   │   │   └── TicketClient.java     # Feign 客户端
│   │   ├── feign/
│   │   │   └── TicketServiceClient.java  # 调用 Python 核心服务
│   │   └── repository/
│   │       ├── AuthRepository.java   # 认证数据抽象接口
│   │       └── ConfigAuthRepository.java  # 配置文件实现
│   ├── resources/
│   │   ├── application.yml
│   │   └── application-dev.yml
│   └── pom.xml
│
├── python-core/                     # Python 核心业务层
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── config.py                # 配置管理
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # API 路由
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── intent.py            # 意图识别模型
│   │   │   ├── order.py             # 订单模型
│   │   │   ├── logistics.py         # 物流模型
│   │   │   └── ticket.py            # 工单模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── intent_recognition.py # 意图识别服务
│   │   │   ├── logistics.py          # 物流查询服务
│   │   │   ├── urgent.py             # 催单服务
│   │   │   └── cancel.py             # 退单服务
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base.py              # 抽象接口
│   │       ├── order_repository.py
│   │       ├── logistics_repository.py
│   │       └── ticket_repository.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── mock_data.py             # 模拟数据
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_intent.py
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   ├── requirements.txt
│   └── .env.example
│
└── docker-compose.yml               # 容器编排
```

## 6. 核心流程时序图

### 6.1 物流查询流程

```
用户 → Intent Router: "我的ORD001到哪了"
Intent Router → Intent Recognition: 识别意图
Intent Recognition → LLM: 结构化输出
LLM → Intent Recognition: {intent: logistics, order_id: ORD001, confidence: 0.95}
Intent Recognition → Intent Router: 路由到物流服务
Intent Router → Logistics Service: 查询ORD001
Logistics Service → Order Repository: 获取订单状态
Order Repository → Logistics Service: {status: shipped}
Logistics Service → Logistics Repository: 获取物流轨迹
Logistics Repository → Logistics Service: [轨迹列表]
Logistics Service → User: 格式化物流信息
```

### 6.2 催单流程

```
用户 → Intent Router: "帮我催一下ORD002"
Intent Router → Intent Recognition: 识别意图
Intent Recognition → LLM: 结构化输出
LLM → Intent Recognition: {intent: urgent, order_id: ORD002, confidence: 0.92}
Intent Recognition → Intent Router: 路由到催单服务
Intent Router → Urgent Service: 创建催单工单
Urgent Service → Ticket Repository: 保存工单
Urgent Service → (Logger): 通知客服
Urgent Service → User: 工单号 + 预计处理时间
```

## 7. 扩展性设计

### 7.1 LLM 可替换
- 通过配置 `LLM_PROVIDER` 切换 OpenAI / Anthropic / 本地模型
- 意图识别提示词模板独立配置

### 7.2 数据源可替换
- 实现 `OrderRepository` 接口即可对接真实业务系统
- 通过依赖注入切换数据源

### 7.3 UI 可替换
- FastAPI 提供 REST API
- Gradio 作为默认 UI，可替换为其他前端
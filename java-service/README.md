# Java Service - 用户层

智能工单系统的用户层，负责认证、会话管理和请求转发。

## 模块职责

- **认证服务**: 用户登录认证，Token 管理
- **会话管理**: 用户会话维护
- **请求转发**: 将请求转发到 Python 核心业务层
- **API 网关**: 统一入口，负载均衡（预留）

## 技术栈

- Spring Boot 3.x
- Spring Cloud OpenFeign - HTTP 客户端
- Maven - 构建工具

## 项目结构

```
java-service/
├── src/main/java/com/smartticket/
│   ├── SmartTicketApplication.java  # 应用入口
│   ├── config/                      # 配置类
│   │   ├── WebConfig.java
│   │   ├── FeignConfig.java
│   │   └── SecurityConfig.java
│   ├── controller/                  # 控制器
│   │   ├── AuthController.java      # 认证接口
│   │   ├── ChatController.java      # 对话接口
│   │   └── HealthController.java    # 健康检查
│   ├── dto/                         # 数据传输对象
│   │   ├── LoginRequest.java
│   │   ├── LoginResponse.java
│   │   ├── ChatRequest.java
│   │   ├── ChatResponse.java
│   │   └── ApiResponse.java
│   ├── service/                     # 服务层
│   │   ├── AuthService.java         # 认证服务接口
│   │   ├── ChatService.java         # 对话服务
│   │   └── impl/
│   │       └── AuthServiceImpl.java # 认证服务实现
│   ├── feign/                       # Feign 客户端
│   │   └── TicketServiceClient.java
│   └── repository/                  # 数据仓库
│       ├── AuthRepository.java      # 认证仓库接口
│       └── ConfigAuthRepository.java # 配置认证实现
├── src/main/resources/
│   ├── application.yml
│   └── application-dev.yml
└── pom.xml
```

## API 端点

### 登录接口
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

# 响应
{
  "success": true,
  "data": {
    "token": "string",
    "user_id": "string",
    "expires_in": 3600
  }
}
```

### 对话接口
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

### 健康检查
```http
GET /health
```

## 配置

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

### 认证用户配置 (application-dev.yml)
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

## 启动服务

```bash
mvn spring-boot:run
```

服务启动后访问 http://localhost:8080

## 认证服务设计

### 抽象接口
```java
public interface AuthService {
    AuthResult authenticate(String username, String password);
    UserInfo getUserByToken(String token);
    boolean validateToken(String token);
    void logout(String token);
}
```

### 认证模式
- **config 模式**: 从配置文件读取用户信息（当前使用）
- **business 模式**: 对接业务系统认证（预留）

## 扩展性

- **认证可扩展**: 实现 AuthRepository 接口对接业务系统
- **微服务改造**: 预留 API Gateway 和服务注册发现接口
- **负载均衡**: 支持多 Python 核心服务实例
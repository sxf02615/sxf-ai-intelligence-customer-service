# Smart Ticket System

智能工单系统 - 基于 LangChain 的智能客服工单系统

## 项目概述

本系统是一个基于 LangChain 的智能客服工单系统，支持三个核心功能：
- **订单物流查询** - 用户输入订单号，查询实时物流状态
- **催单** - 用户催促订单处理，系统创建工单通知客服
- **退单** - 用户取消订单，系统校验并处理退款

## 系统架构

系统采用三层架构设计：

```
┌─────────────────────────────────────────┐
│         UI Layer (Python FastAPI)       │
│         python-ui (端口 8001)            │
└─────────────────┬───────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────┐
│      User Layer (Java Spring Boot)      │
│         java-service (端口 8080)         │
└─────────────────┬───────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────┐
│    Core Business Layer (Python)         │
│        python-core (端口 8000)           │
└─────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术栈 |
|------|--------|
| UI 层 | Python FastAPI + HTML + JavaScript |
| 用户层 | Java Spring Boot 3.x |
| 核心业务层 | Python 3.9+ + FastAPI + LangChain |
| AI 框架 | LangChain + OpenAI API |
| 数据验证 | Pydantic |

## 核心功能

### 1. 意图识别
- 使用 LangChain + Pydantic 进行结构化输出
- 识别三种意图：logistics(物流查询)、urgent(催单)、cancel(退单)
- 提取订单号实体（格式：ORD+数字）
- 置信度低于 0.7 时返回澄清问题

### 2. 物流查询
- 输入订单号查询订单状态
- 已发货订单查询物流轨迹
- 返回格式化物流信息（最新状态、预计送达、最近3条轨迹）

### 3. 催单
- 多轮对话收集订单号和催单原因
- 创建工单并保存
- 通知客服（打印日志模拟）
- 返回工单号、预计处理时间、客服联系方式

### 4. 退单
- 多轮对话收集订单号和退单原因
- 校验订单状态（已取消/已签收/其他）
- 处理退款并返回结果

## 快速开始

### 前置要求

- Python 3.9+
- Java 17+
- Docker & Docker Compose (可选)

### 使用 Docker Compose 启动

```bash
docker-compose up -d
```

服务启动后：
- UI 界面: http://localhost:8001
- Java 服务: http://localhost:8080
- Python 核心服务: http://localhost:8000

### 手动启动

1. **启动 Python 核心服务**
```bash
cd python-core
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置 OpenAI API Key
uvicorn app.main:app --reload --port 8000
```

2. **启动 Java 服务**
```bash
cd java-service
mvn spring-boot:run
```

3. **启动 Python UI**
```bash
cd python-ui
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置 Java 服务地址
uvicorn app.main:app --reload --port 8001
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## 测试订单号

- ORD001 - 已发货 (shipped)
- ORD002 - 已签收 (delivered)
- ORD003 - 已取消 (cancelled)

## 项目结构

```
smart-ticket-system/
├── python-core/          # 核心业务层
├── java-service/         # 用户层
├── python-ui/            # UI 层
├── docker-compose.yml    # 容器编排
└── README.md
```

## 各模块文档

- [python-core 模块](./python-core/README.md)
- [java-service 模块](./java-service/README.md)
- [python-ui 模块](./python-ui/README.md)
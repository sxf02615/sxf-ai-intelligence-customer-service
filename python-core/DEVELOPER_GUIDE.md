# 智能工单系统 - 开发手册

## 目录

1. [系统概述](#系统概述)
2. [核心功能](#核心功能)
3. [技术架构](#技术架构)
4. [上下文管理](#上下文管理)
5. [API 接口](#api-接口)
6. [配置说明](#配置说明)
7. [开发指南](#开发指南)
8. [测试指南](#测试指南)
9. [部署指南](#部署指南)
10. [故障排查](#故障排查)

---

## 系统概述

智能工单系统是一个基于大语言模型（LLM）的智能客服系统，支持自然语言对话，自动识别用户意图并处理物流查询、催单、取消订单等业务。

### 核心特性

- ✅ **智能意图识别**：基于 LangChain + Pydantic 的结构化输出
- ✅ **多轮对话管理**：智能上下文管理，支持灵活的对话顺序
- ✅ **多 LLM 支持**：支持 OpenAI、DeepSeek、豆包、通义千问等
- ✅ **错误恢复**：订单不存在时自动保持意图，允许重试
- ✅ **灵活对话顺序**：支持先意图后订单号，或先订单号后意图
- ✅ **数据抽象层**：Repository 模式，易于对接真实业务系统

### 支持的业务场景

1. **物流查询**：查询订单状态、物流轨迹、预计送达时间
2. **催单服务**：创建催单工单，通知客服处理
3. **取消订单**：验证订单状态，处理退款

---

## 核心功能

### 1. 意图识别

使用 LangChain 和 Pydantic 进行结构化意图识别：

```python
class IntentResult(BaseModel):
    intent: IntentType  # logistics, urgent, cancel
    confidence: float   # 置信度 0-1
    entities: IntentEntities  # 提取的实体（订单号、详情）
    needs_clarification: bool  # 是否需要澄清
    clarification_question: Optional[str]  # 澄清问题
```

**支持的意图类型**：
- `logistics`：物流查询
- `urgent`：催单
- `cancel`：取消订单

### 2. 上下文管理

系统实现了智能的多轮对话上下文管理：

#### 2.1 基本上下文管理

```python
context = {
    "pending_order_id": "ORD001",  # 待处理的订单号
    "pending_intent": "urgent"      # 待处理的意图
}
```

#### 2.2 支持的对话顺序

**顺序1：先意图后订单号**
```
用户: 我想催单
系统: 请提供订单号
用户: ORD001
系统: 已创建催单工单 ✅
```

**顺序2：先订单号后意图**
```
用户: ORD001
系统: 请问您想做什么？查询物流、催单还是取消订单？
用户: 催单
系统: 已创建催单工单 ✅
```

**顺序3：一次性提供完整信息**
```
用户: 帮我催一下订单ORD001
系统: 已创建催单工单 ✅
```

#### 2.3 错误恢复

**订单不存在重试**
```
用户: 我想催单
系统: 请提供订单号
用户: ORD999 (不存在)
系统: 订单不存在，请重新提供
用户: ORD001
系统: 已创建催单工单 ✅
```

#### 2.4 意图变更

**用户可以改变意图**
```
用户: ORD002
系统: 请问您是想查询订单ORD002的物流状态吗？
用户: 我想催单
系统: 已创建催单工单 ✅
```

### 3. 澄清逻辑

系统会在以下情况请求澄清：

1. **置信度低**：意图识别置信度 < 0.7
2. **缺少信息**：缺少订单号或意图
3. **意图不明确**：用户回答模糊

**澄清处理策略**：
- 如果有保存的订单号 + 用户说确认词 → 使用保存的信息
- 如果有保存的订单号 + 用户提供明确意图 → 使用保存的订单号 + 新意图
- 否则 → 返回澄清问题

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│                  (Web UI / Mobile App)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层                              │
│                    (FastAPI Routes)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                     业务服务层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 意图识别服务  │  │  物流服务    │  │  催单服务    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ 取消订单服务  │  │  上下文管理  │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据抽象层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OrderRepo    │  │ LogisticsRepo│  │ TicketRepo   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│              (Mock Data / Database)                         │
└─────────────────────────────────────────────────────────────┘

                      ↕
┌─────────────────────────────────────────────────────────────┐
│                      LLM 层                                  │
│    OpenAI / DeepSeek / 豆包 / 通义千问                       │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
python-core/
├── app/
│   ├── api/                      # API 路由层
│   │   ├── routes.py            # 主路由（聊天、物流、催单、取消）
│   │   └── __init__.py
│   ├── config.py                # 配置管理
│   ├── main.py                  # 应用入口
│   ├── models/                  # 数据模型
│   │   └── __init__.py         # IntentType, Order, Ticket 等
│   ├── repositories/            # 数据抽象层
│   │   ├── base.py             # Repository 接口定义
│   │   └── __init__.py
│   └── services/                # 业务服务层
│       ├── intent_recognition.py  # 意图识别服务
│       ├── llm_factory.py        # LLM 工厂
│       ├── logistics.py          # 物流查询服务
│       ├── urgent.py             # 催单服务
│       ├── cancel.py             # 取消订单服务
│       └── __init__.py
├── data/
│   ├── mock_data.py             # Mock 数据实现
│   └── __init__.py
├── tests/                       # 测试文件
│   ├── test_context_optimization.py
│   ├── test_order_not_found_retry.py
│   ├── test_order_first_intent_second.py
│   ├── test_order_then_different_intent.py
│   ├── test_exact_scenario.py
│   └── test_all_context_scenarios.py
├── docs/                        # 文档
│   ├── CONTEXT_OPTIMIZATION.md
│   ├── INTENT_PERSISTENCE_FIX.md
│   ├── ORDER_ID_PERSISTENCE_FIX.md
│   ├── ORDER_FIRST_INTENT_SECOND.md
│   ├── CLARIFICATION_LOGIC_FIX.md
│   └── CONTEXT_MANAGEMENT_SUMMARY.md
├── .env.example                 # 环境变量示例
├── requirements.txt             # Python 依赖
├── Dockerfile                   # Docker 配置
├── README.md                    # 项目说明（中文）
├── README-en.md                 # 项目说明（英文）
└── DEVELOPER_GUIDE.md          # 本文档
```

---

## 上下文管理

### 上下文状态机

```
┌─────────────────────────────────────────────────────────────┐
│                        初始状态                              │
│              pending_intent: None                           │
│              pending_order_id: None                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  有意图缺订单  │   │  有订单缺意图  │
│  intent: X    │   │  intent: None │
│  order: None  │   │  order: X     │
└───────┬───────┘   └───────┬───────┘
        │                   │
        │  提供订单号        │  提供意图
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   订单验证       │
        └─────────┬───────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  订单存在     │   │  订单不存在    │
│  → 处理请求   │   │  → 清空订单号  │
│               │   │  → 保持意图    │
└───────────────┘   └───────┬───────┘
                            │
                            │  重新提供订单号
                            │
                            └──────────┐
                                       │
                                       ▼
                            ┌─────────────────┐
                            │   订单验证       │
                            └─────────────────┘
```

### 上下文处理逻辑

```python
# 步骤1：检查上下文
saved_order_id = context.get("pending_order_id")
saved_intent = context.get("pending_intent")

# 步骤2：根据上下文决定处理策略
if saved_intent and not saved_order_id:
    # 场景1：有意图，缺订单号 → 只提取订单号
    # 使用保存的意图，避免重新识别
    
elif saved_order_id:
    # 场景2：有订单号（无论是否有意图）→ 识别意图
    # 使用保存的订单号（除非当前消息提供了新订单号）
    
else:
    # 场景3：正常识别意图和订单号
    
# 步骤3：处理澄清逻辑
if needs_clarification:
    if saved_order_id and _is_confirmation(message):
        # 用户确认 → 使用保存的信息
    elif saved_order_id and confidence >= 0.7:
        # 明确意图 → 使用保存的订单号 + 新意图
    else:
        # 返回澄清问题
```

---

## API 接口

### 1. 聊天接口

**端点**：`POST /api/v1/chat`

**请求**：
```json
{
  "session_id": "session_123",
  "user_id": "user_456",
  "message": "我想催单",
  "context": {
    "pending_order_id": null,
    "pending_intent": null
  }
}
```

**响应**：
```json
{
  "success": true,
  "response": "请提供您要催单的订单号",
  "intent": "urgent",
  "session_id": "session_123",
  "needs_clarification": true,
  "clarification_question": "请提供订单号",
  "context": {
    "pending_order_id": null,
    "pending_intent": "urgent"
  }
}
```

### 2. 物流查询接口

**端点**：`GET /api/v1/logistics/{order_id}`

**响应**：
```json
{
  "success": true,
  "data": {
    "order_id": "ORD001",
    "status": "shipped",
    "latest_status": "运输中",
    "estimated_delivery": "2024-01-15T18:00:00",
    "tracking_history": [
      {
        "status": "已发货",
        "timestamp": "2024-01-10T10:00:00",
        "location": "北京"
      }
    ]
  }
}
```

### 3. 催单接口

**端点**：`POST /api/v1/tickets/urgent`

**请求**：
```json
{
  "order_id": "ORD001",
  "reason": "订单已经3天了还没发货"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "ticket_id": "TKT1234567890",
    "order_id": "ORD001",
    "estimated_processing_time": "2-4小时",
    "contact": "400-123-4567"
  }
}
```

### 4. 取消订单接口

**端点**：`POST /api/v1/orders/cancel`

**请求**：
```json
{
  "order_id": "ORD001",
  "reason": "不想要了"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "order_id": "ORD001",
    "refund_amount": 299.00,
    "refund_arrival_time": "2024-01-20",
    "message": "订单已取消，退款将在3-5个工作日内到账"
  }
}
```

---

## 配置说明

### 环境变量

创建 `.env` 文件：

```bash
# ===== LLM 配置 =====
# 提供商选择: openai, deepseek, doubao, qwen
LLM_PROVIDER=openai

# OpenAI 配置
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选

# DeepSeek 配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1  # 可选

# 豆包配置
DOUBAO_API_KEY=your-doubao-api-key
DOUBAO_MODEL=Doubao-pro-32k
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3  # 可选

# 通义千问配置
QWEN_API_KEY=your-qwen-api-key
QWEN_MODEL=qwen-turbo
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # 可选

# ===== 意图识别配置 =====
INTENT_CONFIDENCE_THRESHOLD=0.7  # 意图识别置信度阈值

# ===== 服务配置 =====
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| LLM_PROVIDER | LLM 提供商 | openai |
| INTENT_CONFIDENCE_THRESHOLD | 意图识别置信度阈值 | 0.7 |
| API_HOST | API 服务地址 | 0.0.0.0 |
| API_PORT | API 服务端口 | 8000 |
| LOG_LEVEL | 日志级别 | INFO |

---

## 开发指南

### 1. 环境搭建

```bash
# 克隆项目
git clone <repository-url>
cd python-core

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 2. 启动开发服务器

```bash
# 启动服务
uvicorn app.main:app --reload --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 3. 添加新的意图类型

**步骤1：定义意图类型**

在 `app/models/__init__.py` 中：

```python
class IntentType(str, Enum):
    LOGISTICS = "logistics"
    URGENT = "urgent"
    CANCEL = "cancel"
    REFUND = "refund"  # 新增
```

**步骤2：更新意图识别提示词**

在 `app/services/intent_recognition.py` 中：

```python
INTENT_CLASSIFICATION_PROMPT = """
意图类型说明:
- logistics: 查询物流
- urgent: 催单
- cancel: 取消订单
- refund: 退款查询  # 新增
"""
```

**步骤3：实现业务服务**

创建 `app/services/refund.py`：

```python
class RefundService:
    def query_refund(self, order_id: str) -> dict:
        # 实现退款查询逻辑
        pass
```

**步骤4：添加路由处理**

在 `app/api/routes.py` 中：

```python
elif intent_result.intent == IntentType.REFUND:
    # 处理退款查询
    result = refund_service.query_refund(order_id)
    # ...
```

### 4. 切换 LLM 提供商

```bash
# 方式1：修改 .env 文件
LLM_PROVIDER=deepseek

# 方式2：环境变量
export LLM_PROVIDER=deepseek

# 方式3：代码中动态切换
from app.services.llm_factory import LLMFactory
llm = LLMFactory.get_llm(provider="deepseek")
```

### 5. 自定义 Repository

实现 `OrderRepository` 接口：

```python
from app.repositories.base import OrderRepository
from app.models import Order

class MySQLOrderRepository(OrderRepository):
    def get_by_id(self, order_id: str) -> Optional[Order]:
        # 从 MySQL 查询订单
        pass
    
    def update_status(self, order_id: str, status: str) -> bool:
        # 更新订单状态
        pass
```

---

## 测试指南

### 运行测试

```bash
# 运行所有测试
python test_all_context_scenarios.py

# 运行单个测试
python test_context_optimization.py
python test_order_not_found_retry.py
python test_order_first_intent_second.py
python test_order_then_different_intent.py
python test_exact_scenario.py
```

### 测试覆盖

| 测试文件 | 测试场景 |
|---------|---------|
| test_context_optimization.py | 基本上下文优化 |
| test_order_not_found_retry.py | 订单不存在重试 |
| test_order_first_intent_second.py | 先订单号后意图 |
| test_order_then_different_intent.py | 订单号+不同意图 |
| test_exact_scenario.py | 具体场景测试 |
| test_all_context_scenarios.py | 综合场景测试 |

### 编写测试

```python
import asyncio
from app.api.routes import ChatRequest, chat_endpoint

async def test_my_scenario():
    # 初始化服务
    # ...
    
    # 第一轮对话
    request1 = ChatRequest(
        session_id="test_session",
        user_id="test_user",
        message="我想催单",
        context=None
    )
    response1 = await chat_endpoint(request1, ...)
    
    # 验证结果
    assert response1.intent == "urgent"
    assert response1.needs_clarification == True

if __name__ == "__main__":
    asyncio.run(test_my_scenario())
```

---

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t smart-ticket-core .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=your-key \
  --name smart-ticket-core \
  smart-ticket-core
```

### Docker Compose 部署

```yaml
version: '3.8'

services:
  python-core:
    build: ./python-core
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./python-core:/app
```

### 生产环境配置

```bash
# 使用 gunicorn
pip install gunicorn

# 启动服务
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

---

## 故障排查

### 常见问题

#### 1. LLM API 调用失败

**症状**：意图识别失败，返回错误

**排查步骤**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看日志中的错误信息
4. 验证 LLM 提供商配置

```bash
# 测试 LLM 连接
python test_deepseek_connection.py
python test_llm_switching.py
```

#### 2. 上下文丢失

**症状**：用户提供订单号后，系统重新请求订单号

**排查步骤**：
1. 检查前端是否正确传递 `context` 参数
2. 确认 `session_id` 是否一致
3. 查看日志中的上下文信息

```python
# 日志示例
logger.info(f"上下文信息: saved_order_id={saved_order_id}, saved_intent={saved_intent}")
```

#### 3. 意图识别不准确

**症状**：系统误判用户意图

**排查步骤**：
1. 检查置信度阈值设置
2. 优化意图识别提示词
3. 查看 LLM 返回的置信度

```bash
# 调整置信度阈值
INTENT_CONFIDENCE_THRESHOLD=0.8
```

#### 4. 订单验证失败

**症状**：订单号格式正确但提示不存在

**排查步骤**：
1. 检查订单号格式（应为 ORD+数字）
2. 确认订单在数据源中存在
3. 查看 Repository 实现

```python
# 订单号格式验证
import re
if not re.match(r'^ORD\d+$', order_id):
    # 格式错误
```

### 日志分析

```bash
# 查看实时日志
tail -f logs/app.log

# 搜索特定会话
grep "session_id=xxx" logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log
```

---

## 性能优化

### 1. LLM 调用优化

- 使用上下文管理减少 LLM 调用次数
- 缓存常见意图识别结果
- 使用更快的 LLM 模型（如 gpt-3.5-turbo）

### 2. 数据库优化

- 为订单号添加索引
- 使用连接池
- 实现查询缓存

### 3. API 性能

- 使用异步处理
- 实现请求限流
- 添加响应缓存

---

## 相关文档

### 核心文档
- [README.md](./README.md) - 项目说明（中文）
- [README-en.md](./README-en.md) - 项目说明（英文）
- [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) - 本文档

### 功能文档
- [CONTEXT_MANAGEMENT_SUMMARY.md](./CONTEXT_MANAGEMENT_SUMMARY.md) - 上下文管理总结
- [CONTEXT_OPTIMIZATION.md](./CONTEXT_OPTIMIZATION.md) - 上下文优化说明
- [INTENT_PERSISTENCE_FIX.md](./INTENT_PERSISTENCE_FIX.md) - 意图持久化修复
- [ORDER_ID_PERSISTENCE_FIX.md](./ORDER_ID_PERSISTENCE_FIX.md) - 订单号持久化修复
- [ORDER_FIRST_INTENT_SECOND.md](./ORDER_FIRST_INTENT_SECOND.md) - 先订单号后意图功能
- [CLARIFICATION_LOGIC_FIX.md](./CLARIFICATION_LOGIC_FIX.md) - 澄清逻辑修复

### 其他文档
- [LLM_SWITCHING_GUIDE.md](./LLM_SWITCHING_GUIDE.md) - LLM 切换指南

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

本项目采用 MIT 许可证。

---

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论组

---

**最后更新**：2024-01-15

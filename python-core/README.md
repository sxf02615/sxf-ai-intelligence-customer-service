# Python Core - 核心业务层

智能工单系统的核心业务层，负责意图识别和业务逻辑处理。

## 模块职责

- **意图识别**: 使用 LangChain + Pydantic 识别用户意图
- **物流查询**: 查询订单状态和物流轨迹
- **催单服务**: 创建工单并通知客服
- **退单服务**: 校验订单状态并处理退款
- **数据抽象层**: 统一的 Repository 接口，支持 Mock/真实数据源切换

## 技术栈

- FastAPI - Web 框架
- LangChain - AI 框架
- Pydantic - 数据验证
- 多 LLM 支持 - OpenAI、DeepSeek、豆包等

## 项目结构

```
python-core/
├── app/
│   ├── api/              # API 路由
│   │   └── routes.py
│   ├── config.py         # 配置管理
│   ├── main.py           # 应用入口
│   ├── models/           # 数据模型
│   ├── repositories/     # 数据抽象层
│   └── services/         # 业务服务
│       ├── intent_recognition.py  # 意图识别
│       ├── logistics.py           # 物流查询
│       ├── urgent.py              # 催单服务
│       └── cancel.py              # 退单服务
├── data/
│   └── mock_data.py      # 模拟数据
├── tests/                # 测试
├── requirements.txt
└── .env.example
```

## API 端点

### 对话接口
```http
POST /api/v1/chat
Content-Type: application/json

{
  "session_id": "string",
  "user_id": "string",
  "message": "string"
}
```

### 物流查询
```http
GET /api/v1/logistics/{order_id}
```

### 催单接口
```http
POST /api/v1/tickets/urgent
Content-Type: application/json

{
  "order_id": "string",
  "reason": "string"
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
```

## 配置

创建 `.env` 文件：

```bash
# LLM 提供商 (openai/deepseek/doubao)
LLM_PROVIDER=openai

# OpenAI 配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# DeepSeek 配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# 豆包配置
DOUBAO_API_KEY=your-doubao-api-key
DOUBAO_MODEL=Doubao-pro-32k
```

## 启动服务

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## 数据模型

### Order (订单)
- order_id: 订单号 (ORD+数字)
- status: 订单状态 (pending/processing/shipped/delivered/cancelled)
- amount: 金额
- created_at: 创建时间

### Ticket (工单)
- ticket_id: 工单号 (TKT+时间戳)
- order_id: 关联订单号
- reason: 催单/退单原因
- priority: 优先级 (low/medium/high)
- status: 工单状态 (open/in_progress/resolved)
- created_at: 创建时间
- estimated_processing_time: 预计处理时间

### LogisticsInfo (物流信息)
- order_id: 订单号
- status: 订单状态
- latest_status: 最新物流状态
- estimated_delivery: 预计送达时间
- tracking_history: 物流轨迹 (最近3条)

## 扩展性

- **多 LLM 支持**: 支持 OpenAI、DeepSeek、豆包等多种大模型，通过 `LLM_PROVIDER` 环境变量切换
- **数据源可替换**: 实现 Repository 接口即可对接真实业务系统
- **意图识别提示词**: 独立配置，可自定义
- **LLM 工厂模式**: 易于扩展新的 LLM 提供商

## LLM 切换指南

详细的使用指南请参考 [LLM_SWITCHING_GUIDE.md](LLM_SWITCHING_GUIDE.md)

### 快速切换示例

```bash
# 切换到 DeepSeek
export LLM_PROVIDER=deepseek

# 切换到豆包
export LLM_PROVIDER=doubao

# 切换回 OpenAI
export LLM_PROVIDER=openai
```
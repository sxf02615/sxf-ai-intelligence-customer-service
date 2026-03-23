# Python Core - 智能工单系统核心服务

[English](./README-en.md) | 简体中文

智能工单系统的核心业务层，基于大语言模型（LLM）实现自然语言对话，自动识别用户意图并处理物流查询、催单、取消订单等业务。

## ✨ 核心特性

- 🤖 **智能意图识别**：基于 LangChain + Pydantic 的结构化输出
- 💬 **多轮对话管理**：智能上下文管理，支持灵活的对话顺序
- 🔄 **错误自动恢复**：订单不存在时自动保持意图，允许重试
- 🎯 **灵活对话顺序**：支持先意图后订单号，或先订单号后意图
- 🌐 **多 LLM 支持**：支持 OpenAI、DeepSeek、豆包、通义千问等
- 🔌 **数据抽象层**：Repository 模式，易于对接真实业务系统

## 📋 支持的业务场景

### 1. 物流查询
查询订单状态、物流轨迹、预计送达时间

### 2. 催单服务
创建催单工单，通知客服处理

### 3. 取消订单
验证订单状态，处理退款

## 🎯 对话示例

### 场景1：先意图后订单号
```
👤 用户: 我想催单
🤖 系统: 请提供订单号
👤 用户: ORD001
🤖 系统: 已为您创建催单工单
```

### 场景2：先订单号后意图
```
👤 用户: ORD001
🤖 系统: 请问您想做什么？查询物流、催单还是取消订单？
👤 用户: 催单
🤖 系统: 已为您创建催单工单
```

### 场景3：订单不存在重试
```
👤 用户: 我想催单
🤖 系统: 请提供订单号
👤 用户: ORD999
🤖 系统: 订单不存在，请重新提供
👤 用户: ORD001
🤖 系统: 已为您创建催单工单
```

### 场景4：一次性提供完整信息
```
👤 用户: 帮我催一下订单ORD001
🤖 系统: 已为您创建催单工单
```

## 🏗️ 技术架构

### 技术栈

- **FastAPI** - 高性能 Web 框架
- **LangChain** - LLM 应用开发框架
- **Pydantic** - 数据验证和结构化输出
- **多 LLM 支持** - OpenAI、DeepSeek、豆包、通义千问等

### 项目结构

```
python-core/
├── app/
│   ├── api/              # API 路由
│   │   └── routes.py    # 聊天、物流、催单、取消接口
│   ├── config.py         # 配置管理
│   ├── main.py           # 应用入口
│   ├── models/           # 数据模型
│   ├── repositories/     # 数据抽象层
│   └── services/         # 业务服务
│       ├── intent_recognition.py  # 意图识别
│       ├── llm_factory.py        # LLM 工厂
│       ├── logistics.py          # 物流查询
│       ├── urgent.py             # 催单服务
│       └── cancel.py             # 取消订单
├── data/
│   └── mock_data.py      # 模拟数据
├── tests/                # 测试文件
├── docs/                 # 文档
├── .env.example          # 环境变量示例
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 配置
├── README.md             # 本文档
├── README-en.md          # 英文文档
└── DEVELOPER_GUIDE.md    # 开发手册
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd python-core

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置 LLM
# 至少需要配置一个 LLM 提供商
```

**最小配置示例**：

```bash
# 使用 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# 或使用 DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 4. 测试接口

```bash
# 测试聊天接口
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "user_id": "test_user",
    "message": "我想催单"
  }'

# 测试物流查询
curl "http://localhost:8000/api/v1/logistics/ORD001"
```

## 📡 API 接口

### 聊天接口

**端点**：`POST /api/v1/chat`

**请求示例**：
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

**响应示例**：
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

### 物流查询接口

**端点**：`GET /api/v1/logistics/{order_id}`

### 催单接口

**端点**：`POST /api/v1/tickets/urgent`

### 取消订单接口

**端点**：`POST /api/v1/orders/cancel`

详细的 API 文档请访问：`http://localhost:8000/docs`

## ⚙️ 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM_PROVIDER | LLM 提供商 (openai/deepseek/doubao/qwen) | openai |
| OPENAI_API_KEY | OpenAI API Key | - |
| OPENAI_MODEL | OpenAI 模型 | gpt-3.5-turbo |
| DEEPSEEK_API_KEY | DeepSeek API Key | - |
| DEEPSEEK_MODEL | DeepSeek 模型 | deepseek-chat |
| INTENT_CONFIDENCE_THRESHOLD | 意图识别置信度阈值 | 0.7 |
| API_PORT | API 服务端口 | 8000 |

### LLM 切换

```bash
# 切换到 DeepSeek
export LLM_PROVIDER=deepseek

# 切换到豆包
export LLM_PROVIDER=doubao

# 切换到通义千问
export LLM_PROVIDER=qwen
```

详细的 LLM 配置请参考：[LLM_SWITCHING_GUIDE.md](./LLM_SWITCHING_GUIDE.md)

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python test_all_context_scenarios.py

# 运行单个测试
python test_context_optimization.py
python test_order_not_found_retry.py
python test_order_first_intent_second.py
```

### 测试覆盖

- ✅ 基本上下文优化
- ✅ 订单不存在重试
- ✅ 先订单号后意图
- ✅ 订单号+不同意图
- ✅ 澄清逻辑处理
- ✅ 综合场景测试

## 🐳 Docker 部署

### 使用 Docker

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

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f python-core
```

## 📚 文档

### 核心文档
- [开发手册](./DEVELOPER_GUIDE.md) - 完整的开发指南
- [English README](./README-en.md) - 英文说明文档

### 功能文档
- [上下文管理总结](./CONTEXT_MANAGEMENT_SUMMARY.md) - 上下文管理完整说明
- [上下文优化](./CONTEXT_OPTIMIZATION.md) - 上下文优化原理
- [意图持久化](./INTENT_PERSISTENCE_FIX.md) - 意图持久化修复
- [订单号持久化](./ORDER_ID_PERSISTENCE_FIX.md) - 订单号持久化修复
- [先订单号后意图](./ORDER_FIRST_INTENT_SECOND.md) - 灵活对话顺序
- [澄清逻辑](./CLARIFICATION_LOGIC_FIX.md) - 澄清逻辑优化

### 其他文档
- [LLM 切换指南](./LLM_SWITCHING_GUIDE.md) - 多 LLM 支持说明

## 🔧 开发指南

### 添加新的意图类型

1. 在 `app/models/__init__.py` 中定义新的意图类型
2. 更新 `app/services/intent_recognition.py` 中的提示词
3. 实现对应的业务服务
4. 在 `app/api/routes.py` 中添加路由处理

详细步骤请参考：[开发手册](./DEVELOPER_GUIDE.md)

### 自定义数据源

实现 `Repository` 接口即可对接真实业务系统：

```python
from app.repositories.base import OrderRepository

class MySQLOrderRepository(OrderRepository):
    def get_by_id(self, order_id: str) -> Optional[Order]:
        # 实现从 MySQL 查询订单
        pass
```

## 🐛 故障排查

### 常见问题

1. **LLM API 调用失败**
   - 检查 API Key 是否正确
   - 检查网络连接
   - 查看日志中的错误信息

2. **上下文丢失**
   - 检查前端是否正确传递 `context` 参数
   - 确认 `session_id` 是否一致

3. **意图识别不准确**
   - 调整置信度阈值
   - 优化意图识别提示词

详细的故障排查请参考：[开发手册 - 故障排查](./DEVELOPER_GUIDE.md#故障排查)

## 📈 性能优化

- ✅ 智能上下文管理减少 30-50% 的 LLM 调用
- ✅ 异步处理提升响应速度
- ✅ 结构化输出提高准确性
- ✅ Repository 模式支持数据缓存

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，请：
- 提交 Issue
- 查看[开发手册](./DEVELOPER_GUIDE.md)
- 阅读相关文档

---

**最后更新**：2024-01-15
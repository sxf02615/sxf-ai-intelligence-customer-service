# LLM 切换使用指南

本文档介绍如何在 Smart Ticket System 中切换不同的大语言模型提供商。

## 支持的 LLM 提供商

1. **OpenAI** - 默认提供商
2. **DeepSeek** - 深度求索
3. **豆包 (Doubao)** - 字节跳动

## 配置方法

### 1. 环境变量配置

复制 `.env.example` 文件为 `.env` 并配置相应的 API 密钥：

```bash
# 复制配置文件
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM Configuration
# Provider: openai, deepseek, doubao
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# Doubao Configuration
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_MODEL=Doubao-pro-32k

# Optional: Custom base URL for LLM (if using custom endpoint)
LLM_BASE_URL=
```

### 2. 切换提供商

要切换 LLM 提供商，只需修改 `LLM_PROVIDER` 环境变量：

```bash
# 切换到 DeepSeek
export LLM_PROVIDER=deepseek

# 切换到豆包
export LLM_PROVIDER=doubao

# 切换回 OpenAI
export LLM_PROVIDER=openai
```

或者在 `.env` 文件中直接修改：

```env
LLM_PROVIDER=deepseek  # 使用 DeepSeek
# 或
LLM_PROVIDER=doubao    # 使用豆包
```

## 代码使用示例

### 1. 使用默认 LLM（根据环境配置）

```python
from app.services.llm_factory import LLMFactory

# 获取默认 LLM 实例
llm = LLMFactory.get_default_llm(temperature=0)

# 使用 LLM
response = llm.invoke("你好，请帮我分析一下这个需求")
```

### 2. 动态创建特定提供商的 LLM

```python
from app.services.llm_factory import LLMFactory
from app.config import LLMProvider

# 创建 DeepSeek LLM
deepseek_llm = LLMFactory.create_llm(
    provider=LLMProvider.DEEPSEEK,
    api_key="your_deepseek_api_key",
    model="deepseek-chat",
    temperature=0
)

# 创建豆包 LLM
doubao_llm = LLMFactory.create_llm(
    provider=LLMProvider.DOUBAO,
    api_key="your_doubao_api_key",
    model="Doubao-pro-32k",
    temperature=0
)
```

### 3. 在意图识别服务中使用

意图识别服务会自动使用配置的 LLM 提供商：

```python
from app.services.intent_recognition import get_intent_recognition_service

# 获取意图识别服务
service = get_intent_recognition_service()

# 识别意图（会自动使用配置的 LLM）
result = service.recognize("我的订单ORD001到哪了？")
print(f"意图: {result.intent.value}")
print(f"订单号: {result.entities.order_id}")
```

## API 密钥获取

### DeepSeek
1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册账号并登录
3. 在控制台获取 API 密钥
4. 免费额度：每月 100 万 tokens

### 豆包 (Doubao)
1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 注册账号并登录
3. 创建应用并获取 API 密钥
4. 免费额度：新用户有试用额度

## 测试脚本

项目包含一个测试脚本，用于验证 LLM 切换功能：

```bash
# 运行测试脚本
cd python-core
python test_llm_switching.py
```

测试脚本会：
1. 测试默认 LLM 创建
2. 测试各提供商 LLM 创建
3. 测试意图识别功能

## 故障排除

### 1. API 密钥错误
```
Error: API key is required for deepseek provider
```
解决方案：检查对应的 API 密钥是否已正确配置。

### 2. 网络连接问题
```
Error: Connection error
```
解决方案：
- 检查网络连接
- 确认 API 端点 URL 是否正确
- 对于国内用户，可能需要配置代理

### 3. 模型不可用
```
Error: Model not found
```
解决方案：检查模型名称是否正确，参考各提供商的文档。

## 性能考虑

1. **响应时间**：不同提供商的响应时间可能不同
2. **成本**：各提供商的定价策略不同，请根据使用量选择
3. **稳定性**：建议在生产环境中配置备用提供商

## 扩展新的提供商

要添加新的 LLM 提供商：

1. 在 `app/config.py` 的 `LLMProvider` 枚举中添加新提供商
2. 在 `app/services/llm_factory.py` 的 `create_llm` 方法中添加处理逻辑
3. 更新环境变量配置

示例：
```python
# 在 LLMProvider 枚举中添加
class LLMProvider(str, Enum):
    # ... 现有提供商
    NEW_PROVIDER = "new_provider"

# 在 create_llm 方法中添加
elif provider == LLMProvider.NEW_PROVIDER:
    new_params = common_params.copy()
    if not base_url:
        new_params["base_url"] = "https://api.new-provider.com/v1"
    return ChatOpenAI(**new_params)
```

## 注意事项

1. 所有提供商都使用 OpenAI 兼容的 API 接口
2. 确保 API 密钥的安全性，不要提交到版本控制
3. 定期检查各提供商的 API 更新和变更
4. 建议在生产环境中监控 LLM 使用情况和成本
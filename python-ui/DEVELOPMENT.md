# Python UI 开发手册

智能工单系统的用户界面层开发文档。

## 项目概述

Python UI 是智能工单系统的前端界面层，基于 FastAPI 构建，提供用户登录和智能客服聊天界面。

## 技术栈

- **FastAPI** - Web 框架，提供 API 和页面路由
- **Jinja2** - 模板引擎，渲染 HTML 页面
- **httpx** - 异步 HTTP 客户端，调用 Java 服务
- **Pydantic** - 数据验证和配置管理

## 项目结构

```
python-ui/
├── app/                    # 应用主目录
│   ├── __init__.py        # 包初始化
│   ├── main.py            # 应用入口，路由定义
│   ├── config.py          # 配置管理
│   ├── api/               # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py        # 认证相关 API
│   │   └── chat.py        # 聊天相关 API
│   ├── services/          # 服务层
│   │   ├── __init__.py
│   │   └── http_client.py # HTTP 客户端服务
│   ├── templates/         # HTML 模板
│   │   ├── login.html     # 登录页面
│   │   └── chat.html      # 聊天页面
│   └── static/            # 静态资源
│       ├── css/
│       │   └── style.css  # 样式文件
│       └── js/
│           └── app.js     # 前端交互逻辑
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── README.md            # 项目说明
└── DEVELOPMENT.md       # 本开发手册
```

## 路由系统

### 页面路由 (main.py)

| 路由 | 方法 | 功能 | 认证要求 |
|------|------|------|----------|
| `/` | GET | 根路径，重定向到登录页 | 无 |
| `/login` | GET | 登录页面 | 已登录用户重定向到聊天页 |
| `/chat` | GET | 聊天页面 | 需要登录，未登录重定向到登录页 |
| `/health` | GET | 健康检查 | 无 |

### API 路由

#### 认证 API (auth.py)
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/session` - 获取会话信息
- `GET /api/auth/me` - 获取当前用户信息（前端兼容）

#### 聊天 API (chat.py)
- `POST /api/chat` - 发送聊天消息

## 页面功能

### 登录页面 (login.html)

**功能特性：**
- 用户名/密码输入验证
- 登录表单提交
- 错误消息显示
- 响应式设计

**交互流程：**
1. 用户访问 `/login`
2. 前端检查是否已登录（通过 cookie）
3. 用户输入用户名密码
4. 提交表单到 `/api/auth/login`
5. 成功：设置 session cookie，跳转到 `/chat`
6. 失败：显示错误消息

**HTML 结构：**
```html
<div class="login-container">
  <form id="loginForm">
    <input type="text" name="username" placeholder="用户名">
    <input type="password" name="password" placeholder="密码">
    <button type="submit">登录</button>
  </form>
  <div id="errorMessage" class="error-message"></div>
</div>
```

### 聊天页面 (chat.html)

**功能特性：**
- 消息显示区域
- 消息输入框和发送按钮
- 意图识别结果显示
- 快速操作按钮
- 用户信息显示
- 登出功能

**交互流程：**
1. 用户访问 `/chat`
2. 前端检查认证状态（调用 `/api/auth/me`）
3. 用户输入消息并发送
4. 消息发送到 `/api/chat`
5. 根据意图类型格式化显示响应
6. 支持物流查询、催单、退单三种意图的格式化显示

**HTML 结构：**
```html
<div class="chat-container">
  <div class="chat-header">
    <div id="userInfo">用户信息</div>
    <button id="logoutBtn">退出</button>
  </div>
  
  <div class="chat-messages" id="chatMessages">
    <!-- 消息显示区域 -->
  </div>
  
  <div class="quick-actions">
    <button class="quick-btn" data-message="我的ORD001到哪了">物流查询</button>
    <button class="quick-btn" data-message="帮我催一下ORD002">催单</button>
    <button class="quick-btn" data-message="我要取消ORD003">退单</button>
  </div>
  
  <form id="chatForm">
    <input type="text" id="chatInput" placeholder="输入消息...">
    <button type="submit" id="sendBtn">发送</button>
  </form>
  
  <div id="loading" class="loading">处理中...</div>
  <div id="typingIndicator" class="typing-indicator">客服正在输入...</div>
  <div id="errorMessage" class="error-message"></div>
</div>
```

## 前端交互逻辑 (app.js)

### ChatApplication 类

**主要方法：**

1. **初始化方法**
   - `init()` - 初始化应用
   - `setupEventListeners()` - 设置事件监听器
   - `checkAuth()` - 检查认证状态

2. **消息处理方法**
   - `handleSubmit(e)` - 处理表单提交
   - `sendMessage(message)` - 发送消息到服务器
   - `addMessage(content, type)` - 添加消息到显示区域
   - `addAssistantMessage(data)` - 添加助手消息（带意图格式化）

3. **意图格式化方法**
   - `formatResponseByIntent(intent, response, data)` - 根据意图格式化响应
   - `formatLogisticsResponse(response, data)` - 格式化物流查询响应
   - `formatUrgentResponse(response, data)` - 格式化催单响应
   - `formatCancelResponse(response, data)` - 格式化退单响应

4. **UI 控制方法**
   - `setLoading(loading)` - 设置加载状态
   - `showTypingIndicator()` - 显示输入指示器
   - `showError(message)` - 显示错误消息
   - `scrollToBottom()` - 滚动到底部

### 意图识别显示

**物流查询 (logistics)：**
- 订单状态卡片
- 物流轨迹时间线
- 预计送达时间

**催单处理 (urgent)：**
- 工单创建成功卡片
- 工单号显示
- 预计处理时间
- 客服联系方式

**退单处理 (cancel)：**
- 取消结果卡片（成功/失败）
- 退款金额显示
- 退款到账时间

## 配置管理

### 环境变量配置

创建 `.env` 文件：

```bash
# Java 服务配置
JAVA_SERVICE_URL=http://localhost:8080
JAVA_SERVICE_TIMEOUT=30

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8001
DEBUG=true
APP_TITLE="Smart Ticket System"

# 会话配置
SESSION_SECRET=your-secret-key-change-in-production
SESSION_COOKIE_NAME=session_id
SESSION_TIMEOUT_MINUTES=60
SESSION_SECURE=false
SESSION_HTTPONLY=true

# 静态文件配置
STATIC_CSS_PATH=css
STATIC_JS_PATH=js
STATIC_IMAGES_PATH=images

# CORS 配置
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

### 配置类结构

```python
class Settings(BaseModel):
    java_service: JavaServiceConfig  # Java 服务配置
    app: AppConfig                   # 应用配置
    session: SessionConfig           # 会话配置
    static_files: StaticFilesConfig  # 静态文件配置
    cors: CORSConfig                 # CORS 配置
```

## 开发指南

### 启动开发服务器

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量示例
cp .env.example .env

# 启动开发服务器
uvicorn app.main:app --reload --port 8001
```

### 添加新页面

1. **创建 HTML 模板**
   ```bash
   touch app/templates/new_page.html
   ```

2. **添加路由到 main.py**
   ```python
   @app.get("/new-page", response_class=HTMLResponse)
   async def new_page(request: Request):
       return templates.TemplateResponse("new_page.html", {"request": request})
   ```

3. **添加静态资源（可选）**
   ```bash
   # 添加 CSS
   touch app/static/css/new_page.css
   
   # 添加 JavaScript
   touch app/static/js/new_page.js
   ```

### 添加新 API 端点

1. **创建 API 模块**
   ```bash
   touch app/api/new_api.py
   ```

2. **定义路由**
   ```python
   router = APIRouter(prefix="/api/new", tags=["new"])
   
   @router.get("/endpoint")
   async def get_endpoint():
       return {"message": "Hello"}
   ```

3. **在 main.py 中包含路由**
   ```python
   from app.api import new_api
   app.include_router(new_api.router)
   ```

## 测试指南

### 单元测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/
```

### 手动测试

1. **启动所有服务**
   ```bash
   # 启动 Python Core (端口 8000)
   cd python-core && uvicorn app.main:app --reload --port 8000
   
   # 启动 Java Service (端口 8080)
   cd java-service && mvn spring-boot:run
   
   # 启动 Python UI (端口 8001)
   cd python-ui && uvicorn app.main:app --reload --port 8001
   ```

2. **测试流程**
   - 访问 http://localhost:8001
   - 使用默认账号登录（admin/admin123 或 user/user123）
   - 测试聊天功能：
     - "我的ORD001到哪了" - 物流查询
     - "帮我催一下ORD002" - 催单
     - "我要取消ORD003" - 退单

## 故障排除

### 常见问题

1. **404 Not Found 错误**
   - 检查路由定义是否正确
   - 确认 API 端点路径
   - 验证静态文件路径

2. **认证失败**
   - 检查 Java 服务是否运行
   - 验证环境变量配置
   - 检查 session cookie 设置

3. **跨域问题**
   - 检查 CORS 配置
   - 验证允许的源和头部

4. **样式/脚本加载失败**
   - 检查静态文件挂载路径
   - 验证文件权限
   - 确认文件路径大小写

### 调试技巧

1. **启用调试模式**
   ```bash
   DEBUG=true uvicorn app.main:app --reload --port 8001
   ```

2. **查看日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **检查网络请求**
   - 使用浏览器开发者工具
   - 查看 Network 标签页
   - 检查请求/响应头

## 扩展指南

### 添加新意图类型

1. **更新前端格式化逻辑**
   ```javascript
   // 在 formatResponseByIntent 中添加新 case
   case 'new_intent':
       formattedHtml = this.formatNewIntentResponse(response, structuredData);
       break;
   ```

2. **添加格式化方法**
   ```javascript
   formatNewIntentResponse(response, data) {
       // 实现新意图的格式化逻辑
   }
   ```

3. **更新意图标签**
   ```javascript
   const intentLabels = {
       'logistics': '📦 物流查询',
       'urgent': '⚡ 催单处理',
       'cancel': '❌ 取消订单',
       'new_intent': '✨ 新意图'
   };
   ```

### 国际化支持

1. **添加语言配置文件**
   ```json
   // app/static/lang/zh-CN.json
   {
       "login": "登录",
       "username": "用户名",
       "password": "密码"
   }
   ```

2. **创建国际化工具**
   ```javascript
   class I18n {
       constructor(lang = 'zh-CN') {
           this.lang = lang;
           this.translations = {};
       }
       
       async load() {
           const response = await fetch(`/static/lang/${this.lang}.json`);
           this.translations = await response.json();
       }
       
       t(key) {
           return this.translations[key] || key;
       }
   }
   ```

## 性能优化

### 前端优化

1. **代码分割**
   ```javascript
   // 动态导入大型模块
   const heavyModule = await import('./heavy-module.js');
   ```

2. **图片优化**
   - 使用 WebP 格式
   - 实现懒加载
   - 压缩图片大小

3. **缓存策略**
   - 设置适当的 HTTP 缓存头
   - 使用 Service Worker
   - 实现本地存储

### 后端优化

1. **数据库连接池**
   ```python
   # 使用连接池管理数据库连接
   ```

2. **缓存机制**
   ```python
   # 实现 Redis 缓存
   ```

3. **异步处理**
   ```python
   # 使用异步 I/O 操作
   ```

## 安全考虑

### 认证安全

1. **Session 安全**
   - 使用 HTTPS 时启用 secure cookie
   - 设置 HttpOnly 防止 XSS
   - 实现 CSRF 保护

2. **密码安全**
   - 不在前端存储密码
   - 使用 HTTPS 传输
   - 实现密码强度验证

### 输入验证

1. **前端验证**
   ```javascript
   // 验证输入格式
   if (!isValidInput(input)) {
       showError('输入格式错误');
       return;
   }
   ```

2. **后端验证**
   ```python
   # 使用 Pydantic 验证
   class UserInput(BaseModel):
       username: str
       password: str
   ```

### 输出编码

1. **防止 XSS**
   ```javascript
   // 转义 HTML 特殊字符
   function escapeHtml(text) {
       const div = document.createElement('div');
       div.textContent = text;
       return div.innerHTML;
   }
   ```

2. **内容安全策略**
   ```html
   <!-- 设置 CSP 头 -->
   <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
   ```

## 部署指南

### 生产环境配置

1. **环境变量**
   ```bash
   # 生产环境 .env
   DEBUG=false
   SESSION_SECURE=true
   SESSION_SECRET=strong-random-secret
   ```

2. **反向代理配置**
   ```nginx
   # Nginx 配置示例
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **进程管理**
   ```bash
   # 使用 systemd 管理服务
   sudo systemctl enable smart-ticket-ui
   sudo systemctl start smart-ticket-ui
   ```

### 监控和日志

1. **日志配置**
   ```python
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

2. **健康检查**
   ```bash
   # 定期检查服务状态
   curl http://localhost:8001/health
   ```

3. **性能监控**
   - 使用 Prometheus 收集指标
   - 配置 Grafana 仪表板
   - 设置告警规则
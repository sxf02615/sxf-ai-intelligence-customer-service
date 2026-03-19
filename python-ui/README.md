# Python UI - 用户界面层

智能工单系统的 UI 层，提供登录和聊天界面。

## 模块职责

- **登录页面**: 用户认证入口
- **聊天界面**: 智能客服交互界面
- **API 代理**: 转发请求到 Java 用户层

## 技术栈

- FastAPI - Web 框架
- Jinja2 - 模板引擎
- httpx - 异步 HTTP 客户端

## 项目结构

```
python-ui/
├── app/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置管理
│   ├── api/              # API 路由
│   │   ├── auth.py       # 认证接口
│   │   └── chat.py       # 聊天接口
│   ├── services/
│   │   └── http_client.py # HTTP 客户端
│   ├── templates/        # HTML 模板
│   │   ├── login.html
│   │   └── chat.html
│   └── static/           # 静态资源
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── requirements.txt
└── .env.example
```

## 页面说明

### 登录页面 (login.html)
- 用户名/密码输入
- 登录按钮
- 错误提示显示

### 聊天页面 (chat.html)
- 消息显示区域
- 消息输入框
- 发送按钮
- 意图识别结果显示
- 加载状态指示

## 配置

创建 `.env` 文件：

```bash
JAVA_SERVICE_URL=http://localhost:8080
SESSION_SECRET=your-secret-key
```

## 启动服务

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

服务启动后访问 http://localhost:8001

## 前端交互流程

1. 用户访问登录页面
2. 输入账号密码，点击登录
3. UI 调用 Java 认证服务
4. 认证成功跳转聊天页面
5. 用户发送消息
6. UI 调用 Java 对话服务
7. Java 转发到 Python 核心处理
8. 返回结果并显示

## 静态资源

- `static/css/style.css` - 页面样式
- `static/js/app.js` - 前端交互逻辑

## 扩展性

- **UI 可替换**: FastAPI 提供 REST API，可替换为其他前端框架
- **主题定制**: CSS 文件可自定义样式
- **功能扩展**: 可添加更多页面和功能
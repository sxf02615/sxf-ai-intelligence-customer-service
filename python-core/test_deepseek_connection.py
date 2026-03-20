"""
测试 DeepSeek API 连接是否通畅
"""
import os
import sys

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

import requests

# 获取配置
api_key = os.getenv("DEEPSEEK_API_KEY", "")
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
base_url = "https://api.deepseek.com/v1"

# 检查代理设置
http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

print(f"API Key: {api_key[:8]}****{api_key[-4:] if len(api_key) > 12 else ''}")
print(f"Model: {model}")
print(f"Base URL: {base_url}")
print(f"HTTP Proxy: {http_proxy or '未设置'}")
print(f"HTTPS Proxy: {https_proxy or '未设置'}")
print("-" * 50)

# 测试连接
url = f"{base_url}/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": model,
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}

# 配置 session，禁用系统代理
session = requests.Session()
session.trust_env = False  # 禁用环境变量中的代理

print("已禁用系统代理")

try:
    print("正在连接 DeepSeek API...")
    response = session.post(url, headers=headers, json=data, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ 连接成功!")
    else:
        print(f"\n❌ 连接失败: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n❌ 连接超时")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 连接错误: {e}")
    print("\n💡 解决方案:")
    print("   1. 在 .env 中设置正确的代理: HTTP_PROXY=http://your-proxy:port")
    print("   2. 或者设置 NO_PROXY=deepseek.com 跳过代理")
except Exception as e:
    print(f"\n❌ 未知错误: {e}")
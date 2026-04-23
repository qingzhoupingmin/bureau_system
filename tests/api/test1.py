# 文件名: test_simple_login.py
import requests

# 第1步：发送请求
response = requests.post(
    "http://127.0.0.1:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)

# 第2步：检查状态
print(f"状态码: {response.status_code}")

# 第3步：打印结果
print(f"响应内容: {response.json()}")

# 第4步：断言（如果不对就报错）
assert response.status_code == 200, "应该是200"
data = response.json()
assert data["code"] == 200, "业务应该成功"
assert "user_id" in data["data"], "应该有user_id"

print("✓ 测试通过！")
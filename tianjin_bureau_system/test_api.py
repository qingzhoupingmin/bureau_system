# -*- coding: utf-8 -*-
"""
API快速测试脚本
用于验证API服务是否正常工作
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")

def test_health():
    """测试健康检查"""
    print("\n🏥 测试健康检查接口")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    return response.status_code == 200

def test_root():
    """测试根路径"""
    print("\n🏠 测试根路径")
    response = requests.get(f"{BASE_URL}/")
    print_response("根路径", response)
    return response.status_code == 200

def test_login():
    """测试登录"""
    print("\n🔐 测试登录接口")

    # 测试成功登录
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    print_response("登录成功", response)

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            return data["data"].get("user_id")

    return None

def test_get_users(user_id: int):
    """测试获取用户列表"""
    print("\n👥 测试获取用户列表")

    # 测试分页
    response = requests.get(
        f"{BASE_URL}/api/users",
        params={"page": 1, "page_size": 5}
    )
    print_response("用户列表（分页）", response)

    return response.status_code == 200

def test_get_user_detail(user_id: int):
    """测试获取用户详情"""
    print("\n👤 测试获取用户详情")

    response = requests.get(f"{BASE_URL}/api/users/{user_id}")
    print_response("用户详情", response)

    return response.status_code == 200

def test_get_organizations():
    """测试获取组织列表"""
    print("\n🏢 测试获取组织列表")

    # 测试分页
    response = requests.get(
        f"{BASE_URL}/api/organizations",
        params={"page": 1, "page_size": 5}
    )
    print_response("组织列表（分页）", response)

    return response.status_code == 200

def test_get_assets():
    """测试获取资产列表"""
    print("\n📦 测试获取资产列表")

    # 测试分页
    response = requests.get(
        f"{BASE_URL}/api/assets",
        params={"page": 1, "page_size": 5}
    )
    print_response("资产列表（分页）", response)

    return response.status_code == 200

def test_get_departments():
    """测试获取机关处室列表"""
    print("\n🏛️  测试获取机关处室列表")

    response = requests.get(f"{BASE_URL}/api/organizations/departments")
    print_response("机关处室列表", response)

    return response.status_code == 200

def test_get_units():
    """测试获取中层单位列表"""
    print("\n🏗️  测试获取中层单位列表")

    response = requests.get(f"{BASE_URL}/api/organizations/units")
    print_response("中层单位列表", response)

    return response.status_code == 200

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("   API服务快速测试")
    print("="*60)
    print(f"   测试地址: {BASE_URL}")
    print("="*60)

    results = []

    # 基础测试
    results.append(("健康检查", test_health()))
    results.append(("根路径", test_root()))

    if not results[0][1] or not results[1][1]:
        print("\n❌ 基础测试失败，请检查API服务是否启动")
        return

    # 认证测试
    user_id = test_login()

    # 用户测试
    if user_id:
        results.append(("获取用户列表", test_get_users(user_id)))
        results.append(("获取用户详情", test_get_user_detail(user_id)))

    # 组织测试
    results.append(("获取组织列表", test_get_organizations()))
    results.append(("获取机关处室", test_get_departments()))
    results.append(("获取中层单位", test_get_units()))

    # 资产测试
    results.append(("获取资产列表", test_get_assets()))

    # 打印测试结果
    print("\n" + "="*60)
    print("   测试结果汇总")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("="*60)
    print(f"总计: {len(results)} 个测试，通过: {passed}，失败: {failed}")
    print("="*60)

    if failed == 0:
        print("\n🎉 所有测试通过！API服务运行正常！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查API服务")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到API服务")
        print(f"请确保API服务已启动: {BASE_URL}")
        print("启动命令: uvicorn api.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
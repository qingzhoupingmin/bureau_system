# -*- coding: utf-8 -*-
"""
测试用例发现模块
- 扫描 tests/api/ 下的测试文件
- 按模块分组解析测试类和测试方法
- 缓存测试结构用于前端展示
"""
import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Any

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests" / "api"
CACHE_FILE = Path(__file__).resolve().parent / "test_cache.json"

# 模块定义：文件前缀 → 显示名称 + 图标
MODULE_MAP: Dict[str, Dict[str, str]] = {
    "auth":          {"name": "认证管理", "icon": "🔐"},
    "users":         {"name": "用户管理", "icon": "👥"},
    "organizations": {"name": "组织架构", "icon": "🏢"},
    "assets":        {"name": "资产管理", "icon": "💻"},
    "budgets":       {"name": "预算管理", "icon": "💰"},
    "documents":     {"name": "公文管理", "icon": "📄"},
    "messages":      {"name": "消息管理", "icon": "💬"},
    "test1":         {"name": "基础测试", "icon": "🧪"},
}


def parse_test_file(filepath: Path) -> List[Dict[str, Any]]:
    """解析一个测试文件，提取测试类和测试方法"""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    test_classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # 检查是否是测试类（继承自 object 或有 Test 前缀）
            if not node.name.startswith("Test"):
                continue

            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("test_"):
                        # 获取第一个文档字符串作为描述
                        docstring = ast.get_docstring(item) or ""
                        methods.append({
                            "name": item.name,
                            "doc": docstring,
                            "line": item.lineno,
                        })

            if methods:
                class_doc = ast.get_docstring(node) or ""
                test_classes.append({
                    "class_name": node.name,
                    "doc": class_doc,
                    "methods": methods,
                    "method_count": len(methods),
                })

    return test_classes


def discover_tests() -> List[Dict[str, Any]]:
    """发现所有测试文件并解析"""
    modules = []

    for filepath in sorted(TESTS_DIR.glob("test_*.py")):
        # 确定模块标识
        fname = filepath.stem  # e.g. test_auth_api
        module_key = fname.replace("test_", "").replace("_api", "").strip("_")
        module_info = MODULE_MAP.get(module_key, {"name": fname, "icon": "📦"})

        test_classes = parse_test_file(filepath)
        if not test_classes:
            continue

        total_tests = sum(cls["method_count"] for cls in test_classes)

        modules.append({
            "module_key": module_key,
            "module_name": module_info["name"],
            "icon": module_info["icon"],
            "file": fname + ".py",
            "filepath": str(filepath),
            "test_classes": test_classes,
            "total_tests": total_tests,
        })

    return modules


def get_test_tree() -> List[Dict[str, Any]]:
    """获取树形测试结构（含选择状态）"""
    modules = discover_tests()
    tree = []
    for mod in modules:
        mod_node = {
            "key": mod["module_key"],
            "label": f"{mod['icon']} {mod['module_name']}",
            "file": mod["file"],
            "total": mod["total_tests"],
            "selected": True,
            "children": [],
        }
        for cls in mod["test_classes"]:
            cls_node = {
                "key": f"{mod['module_key']}.{cls['class_name']}",
                "label": cls["class_name"],
                "doc": cls["doc"],
                "selected": True,
                "children": [
                    {
                        "key": f"{mod['module_key']}.{cls['class_name']}.{m['name']}",
                        "label": m["name"],
                        "doc": m["doc"],
                        "line": m["line"],
                        "selected": True,
                    }
                    for m in cls["methods"]
                ],
            }
            mod_node["children"].append(cls_node)
        tree.append(mod_node)
    return tree


def get_pytest_args(selected_keys: List[str] = None) -> List[str]:
    """根据选中的测试键生成 pytest 命令行参数"""
    if not selected_keys:
        return [str(TESTS_DIR)]

    def _test_path(mod_key: str) -> str:
        """获取测试文件路径，支持 test1 等特殊情况"""
        # test1 对应 test1.py 而非 test_test1_api.py
        if mod_key == "test1":
            return str(TESTS_DIR / "test1.py")
        return str(TESTS_DIR / f"test_{mod_key}_api.py")

    # 转换键名为 pytest 选择器
    markers = []
    for key in selected_keys:
        parts = key.split(".")
        if len(parts) == 1:
            markers.append(_test_path(parts[0]))
        elif len(parts) == 2:
            mod_key, class_name = parts
            markers.append(f"{_test_path(mod_key)}::{class_name}")
        elif len(parts) == 3:
            mod_key, class_name, method = parts
            markers.append(f"{_test_path(mod_key)}::{class_name}::{method}")

    return markers


if __name__ == "__main__":
    import json
    tree = get_test_tree()
    print(json.dumps(tree, ensure_ascii=False, indent=2))
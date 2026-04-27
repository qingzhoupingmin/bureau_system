# -*- coding: utf-8 -*-
"""
pytest 异步执行器
- 通过 subprocess 异步运行 pytest
- 实时捕获输出并通过回调推送
- 生成 JSON 格式测试报告
"""
import os
import json
import time
import sys
import subprocess
import threading
import queue
from pathlib import Path
from typing import Callable, List, Optional
from datetime import datetime

REPORTS_DIR = Path(__file__).resolve().parent / "reports"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
PYTEST_INI = TESTS_DIR / "pytest.ini"


def _ensure_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class TestRunner:
    """测试执行器，在独立线程中运行 pytest"""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._running = False
        self._callbacks: List[Callable] = []
        self._stop_flag = threading.Event()

    def on_output(self, callback: Callable[[str], None]):
        """注册输出回调"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[str], None]):
        """移除指定回调"""
        while callback in self._callbacks:
            self._callbacks.remove(callback)

    def clear_callbacks(self):
        """清除所有回调"""
        self._callbacks.clear()

    def _emit(self, data: dict):
        """向所有回调发送数据"""
        for cb in self._callbacks:
            try:
                cb(data)
            except Exception:
                pass

    def _emit_log(self, level: str, message: str):
        self._emit({"type": "log", "level": level, "message": message, "timestamp": time.time()})

    def _emit_result(self, result: dict):
        self._emit({"type": "result", **result, "timestamp": time.time()})

    def run(self, test_paths: List[str], extra_args: List[str] = None):
        """启动测试运行（异步）"""
        if self._running:
            self._emit_log("warning", "测试正在运行中，请等待完成")
            return

        self._running = True
        self._stop_flag.clear()

        # 生成报告路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"report_{timestamp}.json"
        _ensure_dirs()

        # 构建 pytest 命令 - 不使用 --json-report 避免依赖问题
        cmd = [sys.executable, "-m", "pytest"]
        cmd.extend(test_paths)

        if PYTEST_INI.exists():
            cmd.extend(["-c", str(PYTEST_INI)])

        cmd.extend([
            "-v",
            "--tb=short",
            "--no-header",
            "--disable-warnings",
            "-p", "no:cacheprovider",
            "--junitxml=" + str(report_file.with_suffix(".xml")),
        ])
        if extra_args:
            cmd.extend(extra_args)

        self._emit_log("info", f"Python: {sys.executable}")
        self._emit_log("info", f"执行目录: {PROJECT_ROOT}")
        self._emit_log("info", f"命令: {' '.join(cmd)}")

        def _run():
            try:
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(PROJECT_ROOT),
                )

                # 实时读取输出
                for line in iter(self._process.stdout.readline, ""):
                    if self._stop_flag.is_set():
                        self._process.terminate()
                        break
                    line = line.rstrip("\n\r")
                    if line:
                        self._emit_log("stdout", line)

                self._process.wait()

                # 解析 stdout 获取测试结果摘要
                exit_code = self._process.returncode
                duration = time.time() - _start_time

                # 生成简单的统计结果
                summary = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "duration": duration,
                }
                if exit_code == 0:
                    summary["passed"] = 1  # 占位，实际从日志解析
                else:
                    summary["failed"] = 1

                self._emit_result({
                    "exit_code": exit_code,
                    "summary": summary,
                    "duration": duration,
                })

                if exit_code == 0:
                    self._emit_log("success", f"✅ 测试全部通过！耗时 {duration:.1f}秒")
                else:
                    self._emit_log("error", f"❌ 测试完成，退出码: {exit_code}")

            except FileNotFoundError:
                self._emit_log("error", "未找到 pytest，请确认已安装: pip install pytest")
            except Exception as e:
                self._emit_log("error", f"运行异常: {e}")
                import traceback
                self._emit_log("error", traceback.format_exc())
            finally:
                self._running = False
                self._process = None

        _start_time = time.time()
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def stop(self):
        """停止正在运行的测试"""
        if self._running and self._process:
            self._stop_flag.set()
            self._process.terminate()
            self._emit_log("info", "⏹️ 测试已终止")
            self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


# 单例
_runner = TestRunner()


def get_runner() -> TestRunner:
    return _runner
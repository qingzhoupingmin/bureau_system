# -*- coding: utf-8 -*-
"""
测试平台 Flask 后端
- API: 获取测试树、启动/停止测试、获取历史
- SSE: 实时推送测试日志
"""
import json
import time
from pathlib import Path
from queue import Queue, Empty
from flask import (
    Flask, jsonify, request, Response,
    render_template,
)

from test_platform.test_discovery import get_test_tree, get_pytest_args
from test_platform.test_runner import get_runner

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent / "templates"),
    static_folder=str(Path(__file__).resolve().parent / "static"),
)

runner = get_runner()

# ========== API 路由 ==========


@app.route("/")
def index():
    """主页面"""
    return render_template("dashboard.html")


@app.route("/api/tests")
def api_get_tests():
    """获取测试用例树"""
    tree = get_test_tree()
    return jsonify({"code": 200, "data": tree})


@app.route("/api/run", methods=["POST"])
def api_run_tests():
    """启动测试执行"""
    body = request.get_json(silent=True) or {}
    selected = body.get("selected", [])
    extra_args = body.get("extra_args", [])

    if runner.is_running:
        return jsonify({"code": 400, "message": "测试正在运行中"}), 400

    # 生成 pytest 路径
    test_paths = get_pytest_args(selected)
    if not test_paths:
        return jsonify({"code": 400, "message": "未选择任何测试用例"}), 400

    runner.run(test_paths, extra_args=extra_args)
    return jsonify({"code": 200, "message": "测试已启动", "test_paths": test_paths})


@app.route("/api/stop", methods=["POST"])
def api_stop_tests():
    """停止测试"""
    runner.stop()
    return jsonify({"code": 200, "message": "测试已停止"})


@app.route("/api/status")
def api_status():
    """获取运行状态"""
    return jsonify({
        "code": 200,
        "data": {
            "is_running": runner.is_running,
        },
    })


@app.route("/api/history")
def api_history():
    """获取测试历史记录"""
    reports_dir = Path(__file__).resolve().parent / "reports"
    history = []

    if reports_dir.exists():
        for f in sorted(reports_dir.glob("report_*.json"), reverse=True)[:20]:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    report = json.load(fh)
                summary = report.get("summary", {})
                history.append({
                    "file": f.name,
                    "time": f.stat().st_mtime,
                    "total": summary.get("total", 0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "skipped": summary.get("skipped", 0),
                    "duration": summary.get("duration", 0),
                    "environment": report.get("environment", {}),
                })
            except Exception:
                continue

    return jsonify({"code": 200, "data": history})


@app.route("/api/report/<report_name>")
def api_get_report(report_name: str):
    """获取指定报告的详细信息"""
    reports_dir = Path(__file__).resolve().parent / "reports"
    report_file = reports_dir / report_name

    if not report_file.exists():
        return jsonify({"code": 404, "message": "报告不存在"}), 404

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"code": 200, "data": data})
    except Exception as e:
        return jsonify({"code": 500, "message": f"读取报告失败: {e}"}), 500


# ========== SSE (Server-Sent Events) ==========


# 用于清理回调的引用容器
_stream_callbacks = []


@app.route("/stream")
def stream():
    """SSE 实时流：推送测试运行日志"""
    q = Queue()

    def callback(data: dict):
        q.put(data)

    runner.on_output(callback)
    _stream_callbacks.append(callback)

    def generate():
        try:
            yield f"data: {json.dumps({'type': 'connected', 'message': '已连接'})}\n\n"
            while True:
                try:
                    data = q.get(timeout=2)
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    if data.get("type") == "result":
                        break
                except Empty:
                    yield f": heartbeat\n\n"
                    if not runner.is_running and q.empty():
                        time.sleep(1)
                        if q.empty():
                            break

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        finally:
            # 清理回调
            runner.remove_callback(callback)
            if callback in _stream_callbacks:
                _stream_callbacks.remove(callback)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ========== 主入口 ==========

if __name__ == "__main__":
    import webbrowser
    port = 5000
    print(f"""
╔══════════════════════════════════════════════╗
║     🧪 天津市市政工程局 - 自动化测试平台      ║
║                                              ║
║     访问地址: http://127.0.0.1:{port}         ║
║                                              ║
║     按 Ctrl+C 停止服务                        ║
╚══════════════════════════════════════════════╝
    """)
    webbrowser.open(f"http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
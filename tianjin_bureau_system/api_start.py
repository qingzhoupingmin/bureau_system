# -*- coding: utf-8 -*-
"""
API服务启动脚本
天津市市政工程局管理系统 - API服务主入口

使用方法：
    python api_start.py
    或
    python api_start.py --port 8000 --reload
"""
import sys
import os
import argparse
import uvicorn

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_api_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1,
    log_level: str = "info",
    web_ui: bool = True
):
    """
    启动API服务

    Args:
        host: 主机地址
        port: 端口号
        reload: 是否自动重载
        workers: 工作进程数
        log_level: 日志级别
        web_ui: 是否启用Web端界面
    """
    print("=" * 60)
    print("   天津市市政工程局管理系统")
    print("=" * 60)
    print(f"   Web端(推荐): http://localhost:{port}/")
    print(f"   API文档:      http://localhost:{port}/docs")
    print(f"   健康检查:      http://localhost:{port}/health")
    if web_ui:
        print("-" * 60)
        print("   Web 前端管理系统已启用（浏览器访问即可）")
    print("=" * 60)
    print()

    if web_ui:
        print("  [提示] 如需开发前端，请另开终端运行:")
        print(f"    cd municipal-system && npm run dev")
        print()

    # 启动API服务
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=log_level,
        access_log=True
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动API服务")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="主机地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="端口号 (默认: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="禁用自动重载"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数 (生产环境建议4，默认: 1)"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别 (默认: info)"
    )

    args = parser.parse_args()

    try:
        start_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            workers=args.workers,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n\n启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
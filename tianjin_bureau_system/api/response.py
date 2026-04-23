# -*- coding: utf-8 -*-
"""
API 响应和错误处理工具
"""
from typing import Any, Optional
from fastapi import HTTPException, status


class APIResponse:
    """统一的API响应格式"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> dict:
        """
        成功响应

        Args:
            data: 响应数据
            message: 响应消息

        Returns:
            标准响应字典
        """
        response = {
            "code": 200,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response

    @staticmethod
    def error(
        message: str,
        code: int = 400,
        detail: Optional[str] = None
    ) -> HTTPException:
        """
        错误响应

        Args:
            message: 错误消息
            code: HTTP状态码
            detail: 详细错误信息

        Returns:
            HTTPException对象
        """
        error_detail = message
        if detail:
            error_detail = f"{message}: {detail}"

        return HTTPException(
            status_code=code,
            detail=error_detail
        )

    @staticmethod
    def not_found(resource: str = "资源") -> HTTPException:
        """资源不存在错误"""
        return APIResponse.error(
            message=f"{resource}不存在",
            code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized(message: str = "未授权访问") -> HTTPException:
        """未授权错误"""
        return APIResponse.error(
            message=message,
            code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(message: str = "权限不足") -> HTTPException:
        """权限不足错误"""
        return APIResponse.error(
            message=message,
            code=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def bad_request(message: str = "请求参数错误") -> HTTPException:
        """请求参数错误"""
        return APIResponse.error(
            message=message,
            code=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def server_error(message: str = "服务器内部错误") -> HTTPException:
        """服务器内部错误"""
        return APIResponse.error(
            message=message,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ValidationError:
    """参数验证工具"""

    @staticmethod
    def validate_required(value: Any, field_name: str):
        """验证必填字段"""
        if value is None or value == "":
            raise APIResponse.bad_request(f"{field_name}不能为空")

    @staticmethod
    def validate_positive(value: int, field_name: str):
        """验证正整数"""
        if value is not None and value <= 0:
            raise APIResponse.bad_request(f"{field_name}必须为正整数")

    @staticmethod
    def validate_email(email: str):
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise APIResponse.bad_request("邮箱格式不正确")

    @staticmethod
    def validate_length(value: str, field_name: str, min_length: int = 0, max_length: int = 100):
        """验证字符串长度"""
        if value is None:
            return

        length = len(value)
        if length < min_length:
            raise APIResponse.bad_request(f"{field_name}长度不能小于{min_length}个字符")
        if length > max_length:
            raise APIResponse.bad_request(f"{field_name}长度不能超过{max_length}个字符")

    @staticmethod
    def validate_in_range(value: Any, field_name: str, valid_values: list):
        """验证值在指定范围内"""
        if value not in valid_values:
            raise APIResponse.bad_request(f"{field_name}必须是以下值之一: {', '.join(map(str, valid_values))}")

    @staticmethod
    def validate_date(date_str: str, field_name: str):
        """验证日期格式"""
        from datetime import datetime
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise APIResponse.bad_request(f"{field_name}格式不正确，应为YYYY-MM-DD")


class DatabaseErrorHandler:
    """数据库错误处理"""

    @staticmethod
    def handle_database_error(e: Exception, operation: str = "数据库操作"):
        """
        处理数据库错误

        Args:
            e: 异常对象
            operation: 操作描述

        Raises:
            HTTPException
        """
        error_message = str(e)

        if "Duplicate entry" in error_message:
            # 唯一键冲突
            field = error_message.split("'")[1] if "'" in error_message else "字段"
            raise APIResponse.bad_request(f"{field}已存在")

        elif "Foreign key constraint fails" in error_message:
            # 外键约束失败
            raise APIResponse.bad_request("关联数据不存在")

        elif "Data too long" in error_message:
            # 数据过长
            raise APIResponse.bad_request("数据长度超过限制")

        elif "Out of range" in error_message:
            # 数值超出范围
            raise APIResponse.bad_request("数值超出允许范围")

        elif "Connection" in error_message or "Timeout" in error_message:
            # 连接或超时错误
            raise APIResponse.server_error("数据库连接失败")

        else:
            # 其他数据库错误
            raise APIResponse.server_error(f"{operation}失败: {error_message}")
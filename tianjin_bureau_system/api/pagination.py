# -*- coding: utf-8 -*-
"""
分页工具
"""
from typing import List, Any, Dict, Tuple
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    code: int = 200
    data: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    @classmethod
    def create(cls, data: List[Any], total: int, params: PaginationParams):
        """创建分页响应"""
        total_pages = (total + params.page_size - 1) // params.page_size if params.page_size > 0 else 0

        return cls(
            data=data,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages
        )


def paginate_query(sql: str, params: Tuple, pagination: PaginationParams) -> Tuple[str, Tuple]:
    """
    为SQL查询添加分页

    Args:
        sql: 原始SQL语句
        params: SQL参数
        pagination: 分页参数

    Returns:
        (分页SQL, 参数)
    """
    paginated_sql = f"{sql} LIMIT %s OFFSET %s"
    paginated_params = params + (pagination.page_size, pagination.offset)
    return paginated_sql, paginated_params


def count_query(sql: str) -> str:
    """
    将查询SQL转换为计数SQL

    Args:
        sql: 原始SQL语句

    Returns:
        计数SQL
    """
    # 移除ORDER BY子句
    sql_without_order = sql.split("ORDER BY")[0]

    # 提取SELECT和FROM之间的内容
    if "SELECT" not in sql_without_order.upper() or "FROM" not in sql_without_order.upper():
        return f"SELECT COUNT(*) as total FROM ({sql_without_order}) as sub"

    select_part = sql_without_order.upper().split("FROM")[0]
    from_part = sql_without_order.split("FROM")[1]

    # 如果已经有聚合函数，直接使用
    if "COUNT(" in select_part or "SUM(" in select_part or "AVG(" in select_part:
        return f"SELECT COUNT(*) as total FROM ({sql_without_order}) as sub"

    # 否则替换SELECT为COUNT
    count_sql = f"SELECT COUNT(*) as total FROM {from_part}"
    return count_sql
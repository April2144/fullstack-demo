# ===== 依赖注入（与第 5 章同一套：分页 + 数据层）=====

from dataclasses import dataclass

from fastapi import Query

from app.store import NoteStore, note_store


@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
        limit: int = Query(20, ge=1, le=100, description='每页条数'),
        offset: int = Query(0, ge=0, description='跳过多少条'),
) -> Pagination:
    """非法 limit（比如 0 或 1000）由框架直接返回 422，路由函数不会被调用。"""
    return Pagination(limit=limit, offset=offset)


def get_store() -> NoteStore:
    """数据层依赖。

    现在返回 SQLite 单例；换成 MySQL 只改 store.py 与这里，
    所有路由的函数签名保持不变 —— 这就是依赖注入的实际收益。
    """
    return note_store

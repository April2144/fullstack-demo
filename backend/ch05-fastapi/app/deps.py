# ===== 对应笔记 5.6 依赖注入与中间件：依赖部分 =====
"""
依赖注入解决的是「这段逻辑好几个路由都要，但不该复制粘贴」。

写法要点：
  1. 依赖就是一个普通函数（或类），参数照常用 Query / Header 声明
  2. 路由用 Depends(get_xxx) 拿到返回值
  3. 依赖里可以直接抛异常 —— 校验失败根本进不到业务函数
  4. 测试时用 app.dependency_overrides 替换掉，不用改业务代码
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Header, Query

from app.errors import BusinessError
from app.store import ItemStore, item_store


@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
        limit: int = Query(10, ge=1, le=100, description='每页条数，最大 100'),
        offset: int = Query(0, ge=0, description='跳过多少条'),
) -> Pagination:
    """分页参数是所有列表接口都要的，抽成依赖后每个路由只写一行。

    校验（ge / le）写在 Query 里，非法值会由框架直接返回 422，业务函数不会被调用。
    """
    return Pagination(limit=limit, offset=offset)


def get_store() -> ItemStore:
    """数据仓库依赖。

    现在返回内存单例；以后换成数据库，只要改这里（或者换成一个读配置的工厂），
    所有路由的签名都不用动。
    """
    return item_store


def require_token(x_token: Optional[str] = Header(None, alias='X-Token')) -> str:
    """鉴权依赖：没带 token 直接 401，业务函数一行鉴权代码都不用写。

    生产环境当然不是比对固定字符串，而是解析 JWT / 查会话表；
    结构是一样的：校验失败 → 抛错 → 请求到此为止。
    """
    if x_token != 'demo-token':
        raise BusinessError('缺少或错误的 X-Token（示例值：demo-token）', code=401)
    return x_token

# ===== 对应笔记 5.4 请求参数与响应模型 =====
"""
Pydantic 模型是 FastAPI 的核心：它同时承担「校验」和「文档」两件事。

命名约定（第 7 章沿用同一套）：
  XxxBase   公共字段
  XxxCreate 创建入参（没有 id）
  Xxx       出参（有 id）
  XxxList   分页容器
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一响应包：成功和失败都是这个形状，前端只写一套解析。"""

    code: int = Field(0, description='0 表示成功')
    message: str = Field('ok')
    data: Optional[T] = Field(None, description='业务数据，出错时为 null')


class HelloOut(BaseModel):
    message: str
    name: str
    times: int = Field(..., description='重复次数，来自查询参数')


class EchoIn(BaseModel):
    """请求体示例：POST 的入参一定要有模型，别直接收 dict。"""

    text: str = Field(..., min_length=1, max_length=200, description='要回显的内容')


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description='名称')
    price: float = Field(..., ge=0, description='价格，单位元，不能为负')
    tags: List[str] = Field(default_factory=list, description='标签')


class ItemCreate(ItemBase):
    model_config = ConfigDict(json_schema_extra={
        'example': {'name': '机械键盘', 'price': 399.0, 'tags': ['硬件']}
    })


class Item(ItemBase):
    id: int


class ItemUpdate(BaseModel):
    """部分更新：三个字段都可选，没传的不动。"""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class ItemPage(BaseModel):
    items: List[Item]
    total: int = Field(..., description='满足条件的总数')
    limit: int
    offset: int

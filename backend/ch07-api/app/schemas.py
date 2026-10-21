# ===== 对应笔记 7.2 请求与响应数据格式 =====
"""
命名与第 5 章保持一致：
  XxxCreate 创建入参 / XxxUpdate 部分更新入参 / Xxx 出参 / XxxPage 分页容器
所有接口的响应统一套 ApiResponse。
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(0, description='0 表示成功，非 0 与 HTTP 状态码一致')
    message: str = Field('ok', description='给人看的说明')
    data: Optional[T] = Field(None, description='业务数据；出错时为 null')


class Health(BaseModel):
    status: str
    version: str
    time: str


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120, description='标题')
    content: str = Field('', max_length=5000, description='正文')
    status: str = Field('draft', pattern='^(draft|published)$', description='draft 草稿 / published 已发布')


class NoteCreate(NoteBase):
    model_config = ConfigDict(json_schema_extra={
        'example': {'title': '一条新笔记', 'content': '正文内容', 'status': 'draft'}
    })


class NoteUpdate(BaseModel):
    """三个字段都可选：没传的字段保持原值。"""

    title: Optional[str] = Field(None, min_length=1, max_length=120)
    content: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, pattern='^(draft|published)$')


class Note(NoteBase):
    id: int
    created_at: str = Field(..., description='ISO 8601，前端可直接 new Date() 解析')
    updated_at: str


class NotePage(BaseModel):
    items: List[Note]
    total: int = Field(..., description='满足条件的总条数，与 items 长度无关')
    limit: int
    offset: int

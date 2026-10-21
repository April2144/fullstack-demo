# ===== 对应笔记 7.1 接口设计 / 7.2 响应格式 =====
"""
笔记资源的标准五个接口。路径用复数名词，动词交给 HTTP 方法。

路由层只做三件事：
  1. 声明参数（校验交给框架）
  2. 调数据层
  3. 拼统一响应包
SQL 一律不出现在这里。
"""

from fastapi import APIRouter, Query, Response, status

from fastapi import Depends

from app.deps import Pagination, get_pagination, get_store
from app.errors import BusinessError
from app.schemas import ApiResponse, Note, NoteCreate, NotePage, NoteUpdate
from app.store import NoteStore

router = APIRouter(prefix='/notes', tags=['笔记'])


@router.get('', response_model=ApiResponse[NotePage], summary='列表：分页 + 状态过滤')
def list_notes(
        status_filter: str = Query(None, alias='status', pattern='^(draft|published)$',
                                   description='按状态过滤'),
        page: Pagination = Depends(get_pagination),
        store: NoteStore = Depends(get_store),
):
    items, total = store.list(page.limit, page.offset, status_filter)
    return ApiResponse(data=NotePage(items=items, total=total, limit=page.limit, offset=page.offset))


@router.get('/{note_id}', response_model=ApiResponse[Note], summary='详情：不存在返回 404')
def get_note(note_id: int, store: NoteStore = Depends(get_store)):
    return ApiResponse(data=store.get(note_id))


@router.post('', response_model=ApiResponse[Note], status_code=status.HTTP_201_CREATED,
             summary='创建：201 + 新资源')
def create_note(payload: NoteCreate, store: NoteStore = Depends(get_store)):
    note = store.create(payload.title, payload.content, payload.status)
    return ApiResponse(message='created', data=note)


@router.put('/{note_id}', response_model=ApiResponse[Note], summary='部分更新：只改传了的字段')
def update_note(note_id: int, payload: NoteUpdate, store: NoteStore = Depends(get_store)):
    # exclude_unset：没传的字段不覆盖成 null
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise BusinessError('没有需要更新的字段', code=400)
    return ApiResponse(message='updated', data=store.update(note_id, fields))


@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除：204 无响应体')
def delete_note(note_id: int, store: NoteStore = Depends(get_store)):
    """204 不带 body，所以这里不套响应包。

    取舍：200 + 响应包 或 204 + 空，二者都对，关键是全项目统一。
    本项目的删除统一 204，前端因此要单独处理一下「没有 JSON 可解析」。
    """
    store.delete(note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

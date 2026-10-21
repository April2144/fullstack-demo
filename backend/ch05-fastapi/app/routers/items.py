# ===== 对应笔记 5.4 请求参数与响应模型 =====
"""
一个标准资源路由该有的五个接口，都在这里：
  GET    /api/items          列表（分页 + 过滤）
  GET    /api/items/{id}     详情
  POST   /api/items          创建
  PUT    /api/items/{id}     部分更新
  DELETE /api/items/{id}     删除

四个参数来源要分清：
  路径参数 Path   —— 资源标识，必填
  查询参数 Query  —— 过滤、分页，可选
  请求体   Model  —— 创建的字段
  请求头   Header —— token 之类（见 hello.py 的 secure 路由）
"""

from fastapi import APIRouter, Depends, Query, Response, status

from app.deps import Pagination, get_pagination, get_store
from app.schemas import ApiResponse, Item, ItemCreate, ItemPage, ItemUpdate
from app.store import ItemStore

router = APIRouter(prefix='/items', tags=['5.4 请求参数与响应'])


@router.get('', response_model=ApiResponse[ItemPage], summary='列表：分页 + 关键字过滤')
def list_items(
        keyword: str = Query(None, max_length=20, description='按名称模糊过滤'),
        page: Pagination = Depends(get_pagination),
        store: ItemStore = Depends(get_store),
):
    items, total = store.list(page.limit, page.offset, keyword)
    return ApiResponse(data=ItemPage(
        items=items, total=total, limit=page.limit, offset=page.offset
    ))


@router.get('/{item_id}', response_model=ApiResponse[Item], summary='详情：不存在返回 404')
def get_item(item_id: int, store: ItemStore = Depends(get_store)):
    # store.get 查不到会抛 BusinessError(404)，这里不需要写 if
    return ApiResponse(data=store.get(item_id))


@router.post('', response_model=ApiResponse[Item], status_code=status.HTTP_201_CREATED,
             summary='创建：请求体由 ItemCreate 校验')
def create_item(payload: ItemCreate, store: ItemStore = Depends(get_store)):
    return ApiResponse(message='created', data=store.create(payload.name, payload.price, payload.tags))


@router.put('/{item_id}', response_model=ApiResponse[Item], summary='部分更新：只改传了的字段')
def update_item(item_id: int, payload: ItemUpdate, store: ItemStore = Depends(get_store)):
    # exclude_unset：没传的字段不会出现在 fields 里，也就不会被覆盖成 null
    fields = payload.model_dump(exclude_unset=True)
    return ApiResponse(message='updated', data=store.update(item_id, fields))


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除：204 无响应体')
def delete_item(item_id: int, store: ItemStore = Depends(get_store)):
    store.delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

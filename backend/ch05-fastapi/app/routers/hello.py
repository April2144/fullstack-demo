# ===== 对应笔记 5.3 路由设计与请求处理 =====
"""
路由 = 「URL 路径 + HTTP 方法」到「函数」的映射。

本文件按顺序演示五件事：
  1. 静态路径 + 查询参数（含默认值与校验）
  2. 请求体（POST）
  3. 路径参数
  4. 路由顺序陷阱：动态路径会吞掉后面的静态路径
  5. 状态码与 204 的用法
"""

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.deps import require_token
from app.schemas import ApiResponse, EchoIn, HelloOut

# prefix 只写资源名，公共的 /api 前缀在 main.py 里统一加
router = APIRouter(prefix='/hello', tags=['5.3 路由与请求'])


@router.get('', response_model=ApiResponse[HelloOut], summary='最简单的 GET：查询参数')
def say_hello(
        name: str = Query('world', min_length=1, max_length=20, description='称呼'),
        times: int = Query(1, ge=1, le=5, description='重复次数'),
):
    """查询参数 = URL 里 ? 后面的部分。

    类型标注就是校验规则：times 传 "abc" 会被框架直接挡成 422，
    函数体里拿到的一定是合法 int。
    """
    message = ' '.join([f'你好，{name}！'] * times)
    return ApiResponse(data=HelloOut(message=message, name=name, times=times))


# ⚠️ 顺序关键：静态路径必须写在动态路径前面，
# 否则 /hello/echo 会被 /hello/{name} 先匹配走，name 变成 "echo"
@router.get('/echo', response_model=ApiResponse[HelloOut], summary='静态路径要写在动态路径之前')
def echo_as_static():
    return ApiResponse(data=HelloOut(message='这条是静态路由 /hello/echo', name='echo', times=1))


@router.post('', response_model=ApiResponse[dict], status_code=status.HTTP_201_CREATED,
             summary='POST + 请求体：创建成功用 201')
def echo_body(payload: EchoIn):
    """请求体必须是 JSON（Content-Type: application/json），字段由 EchoIn 约束。"""
    return ApiResponse(code=0, message='created', data={'echo': payload.text, 'length': len(payload.text)})


@router.get('/{name}', response_model=ApiResponse[HelloOut], summary='路径参数：写在 URL 里')
def greet(
        name: str = Path(..., min_length=1, max_length=20, description='称呼'),
        times: int = Query(1, ge=1, le=5),
):
    """路径参数是资源标识的一部分，必须传；校验规则写在 Path() 里。"""
    return ApiResponse(data=HelloOut(message=' '.join([f'{name}，你好！'] * times), name=name, times=times))


@router.delete('/{name}', status_code=status.HTTP_204_NO_CONTENT, summary='204：成功但没有响应体')
def forget(name: str):
    """删除类操作用 204。

    注意：返回 204 时不能带 body，所以这里返回 Response 而不是 ApiResponse ——
    全项目要么统一 204，要么统一 200 + 响应包，别混着来（第 7 章有同样的取舍说明）。
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/secure/profile', response_model=ApiResponse[dict], summary='依赖注入：带 token 才放行')
def profile(token: str = Depends(require_token)):
    """require_token 抛错时请求到此为止，业务函数根本不会执行。"""
    return ApiResponse(data={'token': token, 'note': '能走到这里，说明 X-Token 校验已通过'})

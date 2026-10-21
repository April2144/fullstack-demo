# ===== 对应笔记 5.5 错误处理与日志 =====
"""
错误分三类，处理方式不同：

  1. 业务错误（BusinessError）—— 可预期，例如「笔记不存在」「没带 token」
     → 返回 4xx，message 直接给用户看
  2. 参数校验错误（RequestValidationError）—— 框架自动抛
     → 返回 422，并告诉前端具体哪个字段不对
  3. 未捕获异常 —— 代码 bug
     → 返回 500，**不要把堆栈返回给用户**，只记日志

统一成 {code, message, data} 之后，前端只写一套解析逻辑。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger('app.error')


class BusinessError(Exception):
    """业务错误：能说清「为什么不行」的错误都该用它，而不是裸抛 HTTPException。

    好处：raise BusinessError('笔记不存在', code=404) 这一行就能表达完整语义，
    且错误格式由注册的处理器统一保证。
    """

    def __init__(self, message, code=400, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


def error_body(code, message, data=None):
    return {'code': code, 'message': message, 'data': data}


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        logger.warning('业务错误 %s %s -> %s %s',
                       request.method, request.url.path, exc.code, exc.message)
        return JSONResponse(status_code=exc.code, content=error_body(exc.code, exc.message, exc.data))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.status_code, str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.info('参数校验失败 %s %s', request.method, request.url.path)
        return JSONResponse(
            status_code=422,
            content=error_body(422, '请求参数校验失败', {'errors': jsonable_encoder(exc.errors())}),
        )

    # 兜底：任何没被上面接住的异常，都别把堆栈吐给用户
    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception('未处理异常 %s %s', request.method, request.url.path)
        return JSONResponse(status_code=500, content=error_body(500, '服务器内部错误，请稍后重试'))

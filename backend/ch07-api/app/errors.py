# ===== 统一错误处理（对应 7.2 的响应格式约定）=====
"""
四类错误，一套输出：

  业务错误 BusinessError   → 4xx，message 给用户看
  参数校验 RequestValidationError → 422，带字段级 errors
  路由/方法错误 HTTPException     → 404 / 405 等，也套上响应包
  未捕获异常                → 500，只记日志，堆栈不出服务器

前端因此只需要判断 code，不用为每个接口写不同的解析。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger('app.error')


class BusinessError(Exception):
    """可预期的错误。raise BusinessError('笔记不存在', code=404) 即可表达完整语义。"""

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
        return JSONResponse(status_code=exc.code,
                            content=error_body(exc.code, exc.message, exc.data))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code,
                            content=error_body(exc.status_code, str(exc.detail)))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.info('参数校验失败 %s %s', request.method, request.url.path)
        return JSONResponse(
            status_code=422,
            content=error_body(422, '请求参数校验失败', {'errors': jsonable_encoder(exc.errors())}),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception('未处理异常 %s %s', request.method, request.url.path)
        return JSONResponse(status_code=500, content=error_body(500, '服务器内部错误，请稍后重试'))

# ===== 请求上下文中间件（与第 5 章一致）=====
"""
每个请求打一个 X-Request-ID，并记录耗时。联调时用户报错，
让他把响应头里的这串 id 给你，就能在日志里精确定位那一次请求。
"""

import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('app.request')


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get('X-Request-ID') or uuid.uuid4().hex[:12]
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            cost_ms = (time.perf_counter() - started) * 1000
            logger.exception('%s %s 未捕获异常，耗时 %.1fms rid=%s',
                             request.method, request.url.path, cost_ms, request_id)
            raise

        cost_ms = (time.perf_counter() - started) * 1000
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time-ms'] = '%.1f' % cost_ms

        logger.info('%s %s -> %s %.1fms rid=%s',
                    request.method, request.url.path, response.status_code, cost_ms, request_id)
        return response

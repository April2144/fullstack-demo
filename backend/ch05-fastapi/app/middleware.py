# ===== 对应笔记 5.6 依赖注入与中间件 =====
"""
中间件 = 包在「所有请求」外面的那一层，适合做横切关注点：
请求 ID、耗时统计、访问日志。

它和依赖注入的分工：
  * 中间件：每个请求都要做，且不关心路由是谁（日志、计时、追踪）
  * 依赖：只有某些路由需要（分页参数、鉴权、数据库会话）
"""

import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('app.request')


class RequestContextMiddleware(BaseHTTPMiddleware):
    """给每个请求分配一个 ID，并记录耗时。

    X-Request-ID 的价值：用户报错时让他把页面上的这串 id 给你，
    就能在日志里精确定位那一次请求，不用靠时间去猜。
    """

    async def dispatch(self, request, call_next):
        # 上游（Nginx / 网关）已经带了就沿用，保证全链路同一个 id
        request_id = request.headers.get('X-Request-ID') or uuid.uuid4().hex[:12]
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            cost_ms = (time.perf_counter() - started) * 1000
            # exception 会带上完整堆栈，500 排查全靠它
            logger.exception('%s %s 未捕获异常，耗时 %.1fms rid=%s',
                             request.method, request.url.path, cost_ms, request_id)
            raise

        cost_ms = (time.perf_counter() - started) * 1000

        # 回写给客户端，出问题时用户能把 id 报给你
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time-ms'] = '%.1f' % cost_ms

        logger.info('%s %s -> %s %.1fms rid=%s',
                    request.method, request.url.path, response.status_code, cost_ms, request_id)
        return response

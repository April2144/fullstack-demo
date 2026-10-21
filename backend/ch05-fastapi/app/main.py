# ===== 对应笔记 5.2 FastAPI 入门与环境搭建 =====
"""
应用装配入口：只做「组装」，不写业务逻辑。

读这个文件应该能一眼看出整个应用的形状：
   日志 → 中间件 → 异常处理 → 路由 → 健康检查
业务细节都在 routers/ 里。
"""

from fastapi import FastAPI

from app import errors
from app.config import settings
from app.logging_config import setup_logging
from app.middleware import RequestContextMiddleware
from app.routers import hello, items

# 必须在创建 app 之前配置日志，否则早期日志会丢
setup_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description='全栈专题第 5 章：Python 基础、FastAPI 入门、路由、模型、错误与依赖注入',
)

# 中间件是「洋葱」：最后 add 的最先执行。
# 这里只有一层，顺序无所谓；多层时（比如 CORS + 日志）要注意谁包谁。
app.add_middleware(RequestContextMiddleware)

# 统一错误格式：业务错误、422、404、未捕获异常
errors.register_exception_handlers(app)

# 路由：/api 前缀统一加，各 router 内部只写资源名
app.include_router(hello.router, prefix=settings.api_prefix)
app.include_router(items.router, prefix=settings.api_prefix)


@app.get('/health', tags=['系统'], summary='探活接口')
def health():
    """部署脚本、监控、负载均衡都靠这个接口判断「服务活着」。"""
    return {'status': 'ok', 'version': settings.version}


@app.get('/', include_in_schema=False)
def index():
    """根路径不参与文档，只给个人看的入口。"""
    return {
        'message': '第 5 章示例已启动',
        'docs': '/docs',
        'try': '/api/hello?name=world',
    }

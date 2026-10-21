# ===== 对应笔记 7.1 – 7.5 应用装配 =====
"""
与第 5 章同一套骨架：
   日志 → 中间件 → 异常处理 → 路由 → 静态页面

本文件只负责组装，业务在 routers/notes.py，数据在 store.py。
"""

import datetime
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import errors
from app.config import BASE_DIR, settings
from app.logging_config import setup_logging
from app.middleware import RequestContextMiddleware
from app.routers import notes
from app.schemas import ApiResponse, Health
from app.store import note_store

setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时建表 + 灌样例数据（替代已废弃的 @app.on_event）。"""
    note_store.init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description='全栈专题第 7 章：接口设计、统一响应、跨域与前后端联调',
    lifespan=lifespan,
)

# 中间件是洋葱结构：后 add 的在外层。
# 请求上下文放在内层，CORS 放外层 —— 保证预检响应也带上跨域头。
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization', 'X-Token'],
    max_age=600,  # 预检结果缓存 10 分钟，少发一次 OPTIONS
)

errors.register_exception_handlers(app)

app.include_router(notes.router, prefix=settings.api_prefix)


# ---------- 系统接口 ----------
@app.get('/api/health', response_model=ApiResponse[Health], tags=['系统'])
def health():
    return ApiResponse(data=Health(
        status='ok',
        version=settings.version,
        time=datetime.datetime.now().isoformat(timespec='seconds'),
    ))


@app.get('/api/debug/request', response_model=ApiResponse[dict], tags=['系统'])
def debug_request(request: Request):
    """回显请求头：调试跨域时能直接看到 Origin 有没有带上。"""
    return ApiResponse(data={
        'origin': request.headers.get('origin'),
        'host': request.headers.get('host'),
        'client': request.client.host if request.client else None,
    })


@app.get('/', include_in_schema=False)
def index():
    return RedirectResponse('/web/')


# ---------- 7.5 联调页面：和接口同源，天然没有跨域问题 ----------
app.mount('/web', StaticFiles(directory=os.path.join(BASE_DIR, 'web'), html=True), name='web')

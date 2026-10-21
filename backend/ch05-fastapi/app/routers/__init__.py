# 路由按资源分文件，一个文件一类资源，别都塞进 main.py
from app.routers import hello, items

__all__ = ['hello', 'items']

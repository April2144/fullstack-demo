# ===== 对应笔记 5.2 FastAPI 入门与环境搭建 =====
"""
启动入口：python3 run.py

为什么包一层，而不直接敲 uvicorn 命令：
  1. 端口、host、是否 reload 都来自 app/config.py，只有一处需要改
  2. 新手记不住 uvicorn 的参数，run.py 让「跑起来」变成一条命令
  3. 部署时仍推荐直接调 uvicorn（见第 8 章的 systemd 配置），参数由 unit 文件固定
"""

import uvicorn

from app.config import settings

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',          # 用字符串而不是 import 对象：--reload 需要能重新导入模块
        host=settings.host,
        port=settings.port,
        reload=settings.debug,   # 仅开发期；线上必须 False
        log_level=settings.log_level.lower(),
    )

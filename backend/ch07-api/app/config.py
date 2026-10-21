# ===== 配置集中管理（与第 5 章同一套写法，只是多了 CORS 与数据库路径）=====

import os
from dataclasses import dataclass

# app/config.py 的上一级就是项目目录（ch07-api/）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class Settings:
    app_name: str = '笔记 API（第 7 章）'
    version: str = '1.0.0'
    api_prefix: str = '/api'

    host: str = '127.0.0.1'
    port: int = 8000
    debug: bool = True
    log_level: str = 'INFO'

    # 数据层：第 7 章先用 SQLite 文件，换成第 6 章的 MySQL 只改数据层
    db_path: str = os.path.join(BASE_DIR, 'notes.db')

    # 7.3 跨域白名单：写具体地址，不要图省事写 '*'
    cors_origins: tuple = (
        'http://localhost:8080',
        'http://127.0.0.1:8080',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    )


settings = Settings()

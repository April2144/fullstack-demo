# ===== 对应笔记 5.2 FastAPI 入门与环境搭建：配置集中管理 =====
"""
所有「可变的数字和字符串」放这里，业务代码不许出现魔法值。

为什么用 dataclass 而不是散落的常量：
  1. 有类型标注，IDE 能补全
  2. frozen=True 防止运行时被误改
  3. 以后要按环境切换，只改这一处或替换这一个对象
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = 'FastAPI 入门示例（第 5 章）'
    version: str = '1.0.0'
    api_prefix: str = '/api'

    # 本地开发默认值；上线时由 systemd 的启动参数覆盖（见第 8 章）
    host: str = '127.0.0.1'
    port: int = 8000

    # True 时开启 --reload（改代码自动重启）。上线必须关掉，否则会反复重启服务
    debug: bool = True

    # 日志级别：开发用 INFO，线上可调成 WARNING 减少噪声
    log_level: str = 'INFO'


settings = Settings()

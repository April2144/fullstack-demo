# ===== 对应笔记 5.5 错误处理与日志 =====
"""
日志只配一次，在应用启动最早期调用。

三个关键决定：
  1. 输出到 stdout，不自己写文件 —— 交给 systemd / journald / 容器收集，
     否则迟早要处理「日志轮转」和「多进程抢同一个文件」
  2. 格式统一带上时间、级别、模块名，排障时能直接看出「谁在什么时候报的」
  3. force=True：重复调用时覆盖已有 handler，避免 --reload 下日志重复打印
"""

import sys
import logging

LOG_FORMAT = '%(asctime)s | %(levelname)-7s | %(name)-18s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 这些第三方库在 INFO 级别话太多，单独压到 WARNING
NOISY_LOGGERS = ('uvicorn.access',)


def setup_logging(level='INFO'):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout,
        force=True,
    )

    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    return logging.getLogger('app')

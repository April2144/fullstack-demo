# ===== 日志配置（与第 5 章完全一致，保持两章可对照阅读）=====

import sys
import logging

LOG_FORMAT = '%(asctime)s | %(levelname)-7s | %(name)-18s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
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

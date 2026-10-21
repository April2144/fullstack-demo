# ===== 启动入口（与第 5 章一致）：python3 run.py =====

import uvicorn

from app.config import settings

if __name__ == '__main__':
    uvicorn.run(
        'app.main:app',
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

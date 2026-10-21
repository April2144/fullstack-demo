# 第 5 章 · 后端语言与框架

对应笔记：`5.1 Python 基础` / `5.2 FastAPI 入门与环境搭建` / `5.3 路由设计与请求处理` /
`5.4 请求参数与响应模型` / `5.5 错误处理与日志` / `5.6 依赖注入与中间件`

## 文件对照

| 笔记 | 文件 | 内容 |
|---|---|---|
| 5.1 | `basics/01_python_basics.py` | 类型标注、容器、推导式、函数默认值陷阱、dataclass、异常、`__main__` |
| 5.1 | `basics/02_stdlib_tour.py` | `json` / `datetime` / `pathlib` / `re` / `Counter`，以及 `None` 与假值的区别 |
| 5.2 | `app/config.py`、`run.py` | 配置集中（`frozen dataclass`）、一键启动 |
| 5.2 | `app/main.py` | 应用装配：日志 → 中间件 → 异常处理 → 路由 → 健康检查 |
| 5.3 | `app/routers/hello.py` | 查询参数、路径参数、请求体、201/204、**静态路由必须写在动态路由前** |
| 5.4 | `app/schemas.py`、`app/routers/items.py` | 入参/出参模型分离、分页容器、部分更新、404 |
| 5.5 | `app/errors.py`、`app/logging_config.py` | 业务错误 / 422 / 404 / 兜底 500、日志格式与输出位置 |
| 5.6 | `app/deps.py`、`app/middleware.py` | 分页依赖、数据仓库依赖、token 依赖；请求 ID 与耗时中间件 |

## 目录结构

```
ch05-fastapi/
├── app/
│   ├── main.py           # 装配入口，不写业务
│   ├── config.py         # 配置唯一来源
│   ├── errors.py         # 四类错误的统一入口
│   ├── logging_config.py # 日志只配一次
│   ├── middleware.py     # 请求 ID + 耗时
│   ├── deps.py           # 依赖：分页 / 仓库 / token
│   ├── schemas.py        # Pydantic 模型
│   ├── store.py          # 内存数据层（第 6 章换数据库）
│   └── routers/
│       ├── hello.py      # 5.3
│       └── items.py      # 5.4
├── basics/               # 5.1 两个可直接运行的脚本
├── run.py                # python3 run.py
└── requirements.txt
```

## 怎么跑

```bash
cd backend/ch05-fastapi
pip install -r requirements.txt

# 5.1：直接看输出，不需要装任何东西
python3 basics/01_python_basics.py
python3 basics/02_stdlib_tour.py

# 5.2 – 5.6：起服务
python3 run.py
# http://127.0.0.1:8000/docs    交互式文档
# http://127.0.0.1:8000/health  探活
```

也可以用 `uvicorn app.main:app --reload`，效果一样。

## 实测输出（节选）

```bash
curl -s "localhost:8000/api/hello?name=世界&times=2"
# {"code":0,"message":"ok","data":{"message":"你好，世界！ 你好，世界！","name":"世界","times":2}}

curl -s localhost:8000/api/items/999
# {"code":404,"message":"商品 999 不存在","data":null}

curl -s -X POST localhost:8000/api/hello -H "Content-Type: application/json" -d '{"text":""}'
# {"code":422,"message":"请求参数校验失败","data":{"errors":[{"type":"string_too_short",...}]}}

curl -s localhost:8000/api/hello/secure/profile
# {"code":401,"message":"缺少或错误的 X-Token（示例值：demo-token）","data":null}

curl -s -H "X-Token: demo-token" localhost:8000/api/hello/secure/profile
# {"code":0,"message":"ok","data":{"token":"demo-token",...}}
```

响应头里会带 `X-Request-ID` 与 `X-Process-Time-ms`，终端日志同时打一行：

```
2026-10-22 00:17:53 | INFO | app.request | GET /health -> 200 0.5ms rid=9c0938359996
```

## 五节各自解决什么

| 小节 | 一句话 |
|---|---|
| 5.1 | Python 里**只有类型标注、没有运行时类型检查**，但 FastAPI 就是靠标注做校验的 |
| 5.2 | `app = FastAPI()` 之后要做的事是**装配**：日志、中间件、异常、路由，业务另放 |
| 5.3 | 路由顺序会咬人：`/hello/{name}` 写在 `/hello/echo` 前面，`echo` 就永远进不来 |
| 5.4 | 入参和出参必须是两个模型；`exclude_unset` 是「部分更新」的关键 |
| 5.5 | 可预期的错用 `BusinessError`，不可预期的错只记日志、不把堆栈返给用户 |
| 5.6 | 中间件管**所有请求**，依赖管**某些路由**；两者别混用 |

## 三个容易踩的点

1. **默认参数别用可变对象**：`def f(bucket=[])` 会在多次调用间累积，5.1 脚本里有反例演示
2. **`except:` 会吞掉 Ctrl+C**：至少写 `except Exception:`，能让程序被正常中断
3. **同步路由里别调阻塞 IO 还声明成 `async def`**：会卡住整个事件循环。本项目的路由都是 `def`，由 FastAPI 放进线程池执行

## 与第 7 章的关系

第 7 章（`backend/ch07-api/`）沿用这里的**同一套骨架**：

```
app/{main,config,errors,logging_config,middleware,deps,schemas,store}.py + app/routers/
```

区别只在于业务：第 7 章把数据层换成 SQLite、加上 CORS 与联调页面，并讨论接口设计与前后端协作。
所以读完这一章再读第 7 章，不用重新认目录结构。

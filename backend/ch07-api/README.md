# 第 7 章 · API 设计与前后端联调

对应笔记：`7.1 FastAPI 接口设计基础` / `7.2 请求与响应数据格式` / `7.3 跨域与代理配置` / `7.4 接口调试工具` / `7.5 前后端联调实战`

## 文件对照

| 笔记 | 文件 | 内容 |
|---|---|---|
| 7.1 | `app/routers/notes.py` | 路由组织、复数路径 + HTTP 方法、201 / 204、`app/store.py` 数据层分离 |
| 7.2 | `app/schemas.py`、`app/errors.py` | Pydantic 模型（创建 / 更新 / 出参分离）、`ApiResponse` 统一响应包、422 字段级错误 |
| 7.3 | `app/main.py` 的 `CORSMiddleware` | 白名单放行、允许的方法与请求头、预检缓存（白名单在 `app/config.py`） |
| 7.4 | `api.http` + `/docs` | REST Client / JetBrains HTTP Client 脚本、Swagger 交互式文档 |
| 7.5 | `web/index.html` + `web/app.js` | 列表 / 筛选 / 新增 / 删除，含 loading、错误态、204 特殊处理 |

## 目录结构（与第 5 章同一套骨架）

```
ch07-api/
├── app/
│   ├── main.py           # 装配：日志 → 中间件 → 异常 → 路由 → 静态页
│   ├── config.py         # 端口、前缀、CORS 白名单、数据库路径
│   ├── errors.py         # BusinessError / 422 / 404 / 500 统一格式
│   ├── logging_config.py # 与第 5 章完全一致
│   ├── middleware.py     # X-Request-ID + 耗时
│   ├── deps.py           # 分页依赖 + 数据层依赖
│   ├── schemas.py        # ApiResponse + Note 系列
│   ├── store.py          # SQLite 数据层（类封装）
│   └── routers/notes.py  # 笔记资源的五个接口
├── web/                  # 7.5 联调页面（由 FastAPI 托管）
├── api.http              # 7.4 调试脚本
├── run.py                # python3 run.py
└── requirements.txt
```

> 与第 5 章对照着看：`main / config / errors / logging_config / middleware / deps` 结构完全相同，
> 差别只在业务（`store.py` 从内存换成 SQLite，`routers/` 从 hello/items 换成 notes，多了 CORS 与 `web/`）。

## 怎么跑

```bash
cd backend/ch07-api
pip install -r requirements.txt
python3 run.py
# 等价写法：uvicorn app.main:app --reload --port 8000
```

| 地址 | 用途 |
|---|---|
| `http://127.0.0.1:8000/web/` | 7.5 联调页面 |
| `http://127.0.0.1:8000/docs` | 7.4 交互式文档（可以点「Try it out」直接发请求） |
| `http://127.0.0.1:8000/api/notes` | 接口本体 |

数据库用标准库 `sqlite3`，首次启动自动建 `notes.db` 并插入 3 条样例，**不需要装 MySQL**。

## 接口一览

| 方法 | 路径 | 成功状态码 | 说明 |
|---|---|---|---|
| GET | `/api/health` | 200 | 探活，返回版本与服务器时间 |
| GET | `/api/notes?status=&limit=&offset=` | 200 | 列表 + 分页，`total` 是满足条件的总数 |
| GET | `/api/notes/{id}` | 200 | 详情，不存在返回 404 |
| POST | `/api/notes` | 201 | 新建 |
| PUT | `/api/notes/{id}` | 200 | 部分更新（只改传了的字段） |
| DELETE | `/api/notes/{id}` | 204 | 删除，无响应体 |
| GET | `/api/debug/request` | 200 | 回显 `Origin` / `Host`，调跨域时看这里 |

### 响应长什么样（实测）

成功：

```json
{"code":0,"message":"ok","data":{"status":"ok","version":"1.0.0","time":"2026-10-22T00:09:23"}}
```

404（业务错误，`data` 为 null）：

```json
{"code":404,"message":"笔记不存在","data":null}
```

422（参数校验失败，错误精确到字段）：

```json
{"code":422,"message":"请求参数校验失败",
 "data":{"errors":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character"}]}}
```

**为什么要统一响应包**：前端只需要认 `code` 和 `data` 两个字段，
不必为每个接口写一套解析；错误提示也能统一交给一个函数处理。

## 7.3 跨域：三个必须记住的事实

1. **同源 = 协议 + 域名 + 端口三者全同**。`localhost:8080` 调 `127.0.0.1:8000` 是跨域，换 `localhost` 也一样跨 —— 端口不同
2. **跨域是浏览器拦的，不是服务器拦的**。curl / Postman 永远不会报跨域，别拿它们证明「接口没问题」
3. **带 `Content-Type: application/json` 的 POST 会先发 `OPTIONS` 预检**。服务器没回 `Access-Control-Allow-*` 头，真正的 POST 根本不会发出

本项目的两种做法：

- **同源（推荐）**：接口自己托管页面（`/web` 由 `StaticFiles` 提供），前端用相对路径，天然无跨域
- **跨域（仅在前后端分离开发时）**：`CORSMiddleware` 白名单放行；生产环境通常再叠一层 Nginx 反向代理，把 `/api` 转到后端，让前后端在浏览器看来同源

## 7.4 怎么调接口

三种方式，按场景选：

| 方式 | 适合 |
|---|---|
| `/docs`（Swagger UI） | 快速试参数、看响应结构，自动带示例值 |
| `api.http` | 存进仓库的调试脚本，改一次复用，可 review |
| `curl` | 写脚本、上服务器排查 |

```bash
curl -s localhost:8000/api/notes?status=published
curl -s -X POST localhost:8000/api/notes -H "Content-Type: application/json" \
     -d '{"title":"联调","status":"draft"}'
```

## 7.5 联调顺序（照着做就不会乱）

1. 先 `GET /api/health`，确认服务和端口通了
2. 再 `GET /api/notes`，确认数据层有数据、字段名和前端约定一致
3. 写「新增」：先看 201 的响应体里有没有 `id`，前端要拿它做后续操作
4. 写「删除」：注意 204 没有响应体，`res.json()` 会直接抛错
5. 最后补筛选/分页，并把 loading、空列表、出错三种状态都覆盖

页面里的错误提示就是按这个顺序做的：加载失败显示在列表下方，创建失败显示在表单下方，
422 时额外把字段错误拼出来。

## 几个设计取舍

- **`PUT` 做部分更新**：严格 REST 里 `PUT` 是全量替换、`PATCH` 才是部分更新。本项目 `PUT` 只改传了的字段，
  与「前端只提交改动的字段」的实际习惯一致；要严格区分就再加一个 `PATCH` 路由
- **删除返回 204**：和统一响应包冲突。二者都对，关键是全项目统一 —— 本项目删除用 204，其余用响应包
- **同步路由 + 线程池**：数据层是阻塞的 `sqlite3`，所以路由写成 `def` 而不是 `async def`，交给 FastAPI 的线程池跑；
  写成 `async def` 里调阻塞 IO 会卡住事件循环
- **`notes.db` 不提交**：已在 `.gitignore` 里排除（`*.db`），每次启动自动重建

## 与其他章节的关系

- 数据层 `app/store.py` 用的是 SQLite；换成第 6 章的 MySQL 只需替换这一层，接口层完全不动
- 部署到服务器后，`--port 8000` 前面要加 Nginx 反向代理，见第 8 章 `deploy/ch08-09/nginx/fullstack.conf`

# 变更记录

> 每行对应「哪几篇笔记 + 哪个 tag」，文章里的链接据此定位。

## v0.1 · 2026-10-21

- 仓库初始化：目录骨架、README 索引、版本对齐约定
- 第 2 章「前端基础」完整示例（tag `ch02`）：
  - `2.1 HTML 结构与常用标签` → `frontend/ch02-basics/01-index.html`
  - `2.2 CSS 基础` → `frontend/ch02-basics/02-style.css`
  - `2.3 JavaScript 核心语法` → `frontend/ch02-basics/03-basics.js`
  - `2.4 DOM 操作与事件处理` → `frontend/ch02-basics/04-dom.js`
  - `2.5 前后端数据交互初探（fetch）` → `frontend/ch02-basics/05-fetch.js`
  - 汇总页：`frontend/ch02-basics/index.html`

## v0.2 · 2026-10-21

以线上专题「全栈开发：从 0 到上线」（`series_id = 5`）为准，补齐第 1、3 章，并对第 2 章做覆盖度补充。

### 新增：第 1 章（tag `ch01`）

- `1.1 什么是全栈开发` → `frontend/ch01-overview/01-request-flow.html`
- `1.2 前后端职责与协作方式` → `frontend/ch01-overview/02-roles.html`
- `1.3 技术栈选型：前端、后端、数据库怎么选` → `frontend/ch01-overview/03-stack.html`
- `1.4 开发环境搭建` → `frontend/ch01-overview/04-env.html`
- `1.5 第一个全栈项目结构预览` → `frontend/ch01-overview/05-structure.html`
- 汇总页 `index.html`、样式 `style.css`、说明 `README.md`

### 新增：第 3 章（tag `ch03`）

- `3.1 页面布局实战` → `01-layout.html`
- `3.2 样式与主题设计` → `02-theme.html` + `02-theme.css` + `02-theme.js`
- `3.3 表单与用户输入` → `03-form.html` + `03-form.js`
- `3.4 动态交互与数据渲染` → `04-render.html` + `04-render.js` + `data/items.json`
- `3.5 响应式设计与移动端适配` → `05-responsive.html` + `05-responsive.css`
- 汇总页 `index.html`、样式 `style.css`（以第 2 章样式为基线复制后扩展，保证本章可单独运行）、说明 `README.md`

### 补充：第 2 章（仅追加，未改动既有代码行）

- `2.1`：新增「常用文本标签与链接」「块级元素与行内元素」
- `2.2`：新增 `display` 四种取值对比、`:hover` / `:first-child` 伪类、`position: relative / absolute` 定位
- `2.3`：新增运算符（含 `??` 与 `||` 的区别）、流程控制（if / 三元 / switch / for / for...of）、字符串常用方法、`try / catch / finally`
- `2.4`：新增显示与隐藏（`hidden` + `aria-expanded` 同步）、实时搜索基础版
- `2.5`：新增 POST / PUT / DELETE 的请求构造、`request()` 封装、跨域说明
- 归属判断：`DocumentFragment` 性能优化、搜索防抖、跨域解法均属进阶，统一留在第 3 章 / 第 7 章，不重复进第 2 章

### 修正：文档

- `README.md` 技术栈 `Python 标准库 + FastAPI + SQLite，不依赖 MySQL` → `Python + FastAPI + MySQL`（与专题 1.3 正文一致）
- `README.md` 目录树与映射表补「导读」「第 1 章」「实战案例」，并补全第 4–14 章的小节范围
- `README.md` 新增「章节数据的唯一来源」，记录专题 id 与核对方式，避免后续凭印象补章节
- `README.md` 运行方式按章分端口（8080 / 8081 / 8082）

### 遗留

- 第 4 章起（`ch04-tooling` / `backend` / `deploy` / `practice`）仍为占位，未预造假代码
- 专题 84 篇中仅 6 篇已发布，其余为草稿/下架状态；上架后需重新核对第 2、3 章正文与 demo 的覆盖度

## v0.3 · 2026-10-21

### 修复

- `frontend/ch02-basics/04-dom.js`：缺目标元素时只打 `console.warn` 却没有中止执行，
  后续 `form.addEventListener` 会抛 `TypeError`。
  脚本顶层不允许 `return`，改为「可选链 + 函数内守卫」：
  `addNoteItem` / `updateCount` 增加 `if (!list) return` / `if (!countHint || !list) return`，
  `form` / `list` 的事件绑定改为 `?.addEventListener`。
- `README.md`：tag 链接曾被误改为 `fullstack-demo`，**已还原为 `fullstack-demo-`**。
  仓库真名确实带尾部短横线（`https://github.com/April2144/fullstack-demo-.git`），不是笔误，v0.2 的「待确认」条目作废。

### 验证

- 构造缺少目标元素的临时页引用 `04-dom.js`：控制台只剩一条 warn，`Uncaught` 为 0（修复前会抛 `TypeError`）
- `ch02-basics/index.html` 回归：笔记 2 条、搜索结果 5 条、远程列表 5 条，功能正常
- 三章共 14 个页面：HTTP 200、控制台报错 0

### 环境同步（线上 → 本地，只动开发库，未碰生产）

- 本地 `site_db` 专题 5 的导读与第 1 章（id `175`、`177`–`181`）按线上内容更新：
  标题、正文、`status`（`0 → 1`）、`updated_at` 与线上**逐字一致**
- 清空上述 5 篇的 `draft_data` 旧草稿缓存（线上这 6 篇 `has_draft` 均为 `False`），
  否则 admin 打开时仍会显示旧草稿
- 同步前备份：`/tmp/learning_articles_backup_20261021_234456.json`（6 行完整数据，可回滚）
- 复核：本地 `GET /site/learning/series/5` → `article_count = 6`（同步前为 1）

### 说明

- 本目录已初始化为 git 仓库（`main`），远端为 `git@github.com:April2144/fullstack-demo-.git`；
  README 第四节的 tag 方案自此具备执行条件（tag 待各章定稿后单独打）

## v0.4 · 2026-10-22

补齐第 4 章与第 6–9 章。小节标题一律取自本地 `site_db`（`learning_chapters` / `learning_articles`，`series_id = 5`），
不按印象补；第 6–9 章文章均为草稿（`status = 0`），标题核对后再落地。

### 新增：第 4 章（`frontend/ch04-tooling/`）

- `4.4 构建与压缩` → `04-build/build.mjs`（零依赖构建：合并 + 去注释 + 压空白）、
  `04-build/src/*`（源文件）、`04-build/04-build.html`；实测 2.44 KB → 1.27 KB（-47.8%）
- `4.5 配置管理` → `05-config/config.js`（三环境配置 + 环境判定）、`05-config/env.js`（只负责渲染）、
  `05-config/05-env.html`（现场切换，支持 `?env=production`）
- 汇总页 `index.html`、说明 `README.md`（补齐后本章导航无死链）

### 新增：第 6 章（`backend/ch06-database/`）

- `6.1 关系型数据库基础` → `README.md` 第一节（表/行/主键/外键/索引、三种关系）
- `6.2 表设计与字段类型` → `schema.mysql.sql`（正文口径）+ `schema.sqlite.sql`（等价方言）、字段类型对照表
- `6.3 SQL 增删改查` → `queries.sql` + `seed.sql`
- `6.4 Python 操作 MySQL` → `crud_demo.py`（一轮 CRUD + 事务回滚 + LEFT JOIN + 先查后删）
- `6.5 数据库连接与配置管理` → `db.py`（配置分层 / 连接工厂 / 事务上下文 / 两后端差异收口）、
  `db_config.example.json`

### 新增：第 7 章（`backend/ch07-api/`）

- `7.1 FastAPI 接口设计基础` → `app/routers/notes.py`（复数路径 + HTTP 方法、201/204）、
  `app/main.py`（`lifespan` 启动钩子）
- `7.2 请求与响应数据格式` → `app/schemas.py`（创建/更新/出参三套模型、`ApiResponse` 统一响应包）、
  `app/errors.py`（422 字段级错误）
- `7.3 跨域与代理配置` → `app/main.py` 的 `CORSMiddleware`（白名单在 `app/config.py`）
  + `/api/debug/request` 回显 `Origin`
- `7.4 接口调试工具` → `api.http`（REST Client 脚本）+ `/docs`
- `7.5 前后端联调实战` → `web/index.html` + `web/app.js`（列表/筛选/新增/删除，204 与错误态处理）
- `app/store.py`（SQLite 数据层，类封装）、`requirements.txt`、`README.md`

### 新增：第 8–9 章（`deploy/ch08-09/`，只读参考）

- 8.2 `cheatsheet.md`；8.3 `scripts/install-python-mysql.sh`；8.4 `nginx/fullstack.conf`；
  8.5 `systemd/fullstack.service`；8.6 `scripts/deploy.sh`
- 9.2 `nginx/https.conf`；9.5 `scripts/healthcheck.sh`
- 8.1 选购清单、9.1 解析、9.3/9.4 备案材料与流程，统一写在 `README.md`
- 脚本均已 `bash -n` 校验并置 `+x`；全部标注「不要在本机执行」

### 验证

- 第 6 章：`python3 crud_demo.py` 退出码 0，事务冲突后 `users` 行数 2 → 2（无脏数据），
  LEFT JOIN 正确带出无标签笔记
- 第 7 章：`GET /api/health`、`/api/notes`、`POST`（201）、`PUT`、`DELETE`（204）逐一实测；
  404 返回 `{"code":404,...}`，422 返回字段级 `errors`；无头浏览器打开 `/web/` 渲染出 3 条数据
- 第 4 章：`node build.mjs` 通过、`node --check dist/bundle.min.js` 通过、6 个页面链接 0 缺失

### 说明（取舍）

- 第 6 章正文口径是 MySQL，但仓库原则是「零配置可跑」，故**默认 SQLite + 同结构 MySQL 版并存**，
  `--backend mysql` 走真实 pymysql；两边共用同一份业务 SQL，方言差异集中在 `db.py`
- 第 8–9 章保持「只读参考」，不做本地可执行的 Nginx 演示（避免要求本机装 nginx）
- 根 `README.md` 同步：章节映射表状态、后端/部署运行方式、编写原则第 1 条改为「默认 SQLite + MySQL 版并存」

## v0.5 · 2026-10-22

补齐第 5 章；第 7 章按第 5 章的骨架重构，两章目录结构自此一致；仓库忽略规则补充。
第 5 章文章标题同样取自本地 `site_db`（第 5 章 6 篇均为草稿）。

### 新增：第 5 章（`backend/ch05-fastapi/`）

- `5.1 Python 基础` → `basics/01_python_basics.py`（标注/容器/推导式/默认参数陷阱/dataclass/异常/`__main__`）、
  `basics/02_stdlib_tour.py`（`json` / `datetime` / `pathlib` / `re` / `Counter`、`None` 与假值）
- `5.2 FastAPI 入门与环境搭建` → `app/config.py`（frozen dataclass）、`app/main.py`（装配）、`run.py`
- `5.3 路由设计与请求处理` → `app/routers/hello.py`（查询/路径/请求体、201/204、静态路由顺序陷阱）
- `5.4 请求参数与响应模型` → `app/schemas.py`、`app/routers/items.py`、`app/store.py`（内存仓库）
- `5.5 错误处理与日志` → `app/errors.py`（业务错误/422/404/500 四类）、`app/logging_config.py`
- `5.6 依赖注入与中间件` → `app/deps.py`（分页/仓库/token 依赖）、`app/middleware.py`（`X-Request-ID` + 耗时）
- `requirements.txt`、`README.md`

### 重构：第 7 章（结构对齐第 5 章）

- 根目录 `main.py` / `schemas.py` / `store.py` **平移**到 `app/` 下，内容无丢失
- 新增 `app/config.py`（CORS 白名单、`db_path`）、`app/errors.py`、`app/logging_config.py`、
  `app/middleware.py`、`app/deps.py`、`app/routers/notes.py`、`run.py`
- `app/store.py` 由函数式改为 `NoteStore` 类封装，供 `deps.get_store()` 注入；`NoteList` 更名为 `NotePage`（与 `ItemPage` 对齐）
- 启动方式统一为 `python3 run.py`（等价 `uvicorn app.main:app`）；`api.http` 与部署文档同步
- v0.4 条目中第 7 章的路径已同步为重构后的实际位置（`app/` 下），无需再对照本节修正

### 变更：仓库约定

- `.gitignore` 新增：`frontend/ch04-tooling/04-build/dist/`（构建产物）、`db_config.json`（含密码）、`*.pem` / `*.key`

### 验证

- 第 5 章：`basics/*.py` 直接运行无报错；`/api/hello`、`/api/hello/echo`（静态优先）、`/api/hello/{name}`、
  `POST`（201）、`422`、无 token（401）/带 token（200）、`/api/items` 五个接口逐一实测；
  响应头含 `X-Request-ID`、`X-Process-Time-ms`，日志按 `rid` 可对应
- 第 7 章重构后：`health` / `list` / `create`(201) / `update` / 空更新(400) / `delete`(204) / `404` / `422` 全通；
  CORS 预检返回 `access-control-allow-origin: http://localhost:8080`；无头浏览器打开 `/web/` 仍渲染出 3 条
- 第 8 章 systemd 的 `ExecStart` 已改为 `app.main:app`，与实际目录一致

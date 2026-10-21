# fullstack-demo

「全栈开发：从 0 到上线」专题的配套演示工程。

> 讲义的每一段代码都能在这里找到完整版本；文章正文只放关键片段。
> 文件顶部统一标注归属笔记编号（如 `对应笔记 2.3`），方便互相查找。

---

## 一、怎么跑

### 前端（第 2–4 章）

**方式一（最简单）**：直接双击各目录下的 `index.html`。

**方式二（推荐，`fetch` 示例需要）**：

```bash
# 第 1 章（纯静态，双击也能看）
cd frontend/ch01-overview && python3 -m http.server 8082

# 第 2 章
cd frontend/ch02-basics && python3 -m http.server 8080

# 第 3 章
cd frontend/ch03-interaction && python3 -m http.server 8081
```

> `2.5 fetch`、`3.4 数据渲染` 必须通过 HTTP 访问；直接双击（`file://`）会被浏览器安全策略拦截。
> 每章一个端口，互不干扰；验证完用 `lsof -ti:8080 | xargs kill` 关掉对应服务。

### 后端（第 5–7 章）

待填充。约定：**Python + FastAPI + MySQL**，不依赖重型框架，`pip install -r requirements.txt` 即可运行。

> 技术栈口径以专题 1.3 正文为准：前端 HTML/CSS/JS、后端 Python + FastAPI、数据库 **MySQL**
> （SQLite 在正文中只作为「小型项目、本地存储」的对比项，不是本专题选型）。

---

## 二、目录

```
fullstack-demo/
├── frontend/
│   ├── ch01-overview/        ✅ 已实现（全栈概述 / 请求流程 / 技术栈 / 环境 / 目录结构）
│   ├── ch02-basics/          ✅ 已实现（HTML / CSS / JS / DOM / fetch）
│   ├── ch03-interaction/     ✅ 已实现（布局 / 主题 / 表单 / 渲染 / 响应式）
│   └── ch04-tooling/         ⏳ 待填充
├── backend/
│   ├── ch05-fastapi/         ⏳ 待填充
│   ├── ch06-database/        ⏳ 待填充
│   └── ch07-api/             ⏳ 待填充
├── deploy/
│   └── ch08-09/              ⏳ 待填充（只读参考，不直接执行）
├── practice/                 ⏳ 第 14 章实战：前端 + SQLite + FastAPI 完整小站
├── README.md                 ← 本文件：索引与约定
└── CHANGELOG.md              ← 每次改动对应哪几篇笔记
```

---

## 三、章节 ↔ 代码 映射

| 章节 | 主题 | 代码目录 | 对应笔记 | 状态 |
|---|---|---|---|---|
| 导读 | 了解专题 | —（无代码） | — | ✅ |
| 第 1 章 | 全栈开发概述与环境准备 | `frontend/ch01-overview/` | 1.1 – 1.5 | ✅ 完成 |
| 第 2 章 | 前端基础 | `frontend/ch02-basics/` | 2.1 – 2.5 | ✅ 完成 |
| 第 3 章 | 页面开发与交互 | `frontend/ch03-interaction/` | 3.1 – 3.5 | ✅ 完成 |
| 第 4 章 | 前端工程化 | `frontend/ch04-tooling/` | 4.1 – 4.5 | ⏳ |
| 第 5 章 | 后端语言与框架 | `backend/ch05-fastapi/` | 5.1 – 5.6 | ⏳ |
| 第 6 章 | 数据库设计与操作 | `backend/ch06-database/` | 6.1 – 6.5 | ⏳ |
| 第 7 章 | API 设计与前后端联调 | `backend/ch07-api/` | 7.1 – 7.5 | ⏳ |
| 第 8 章 | 服务器与部署 | `deploy/ch08-09/` | 8.1 – 8.6 | ⏳ |
| 第 9 章 | 域名、HTTPS 与备案 | `deploy/ch08-09/` | 9.1 – 9.5 | ⏳ |
| 第 10 章 | 架构设计与性能优化 | 待定 | 10.1 – 10.5 | ⏳ |
| 第 11 章 | 安全与权限控制 | 待定 | 11.1 – 11.5 | ⏳ |
| 第 12 章 | 缓存与高并发 | 待定 | 12.1 – 12.5 | ⏳ |
| 第 13 章 | 自动化部署与 CI/CD | 待定 | 13.1 – 13.5 | ⏳ |
| 第 14 章 | 全栈项目实战 | `practice/` | 14.1 – 14.6 | ⏳ |
| 实战案例 | 这个网站是怎么搭出来的 | —（10 篇标题待定） | — | ⏳ |

> 文章级（小节级）映射在每章目录的 `README.md` 里维护，随该章写作推进补齐。

### 章节数据的唯一来源

上表的章节与小节数**以线上专题为准**，不凭印象补：

- 专题：`全栈开发：从 0 到上线`（`series_id = 5`），共 **16 个章节单元、84 篇文章**
- 公开接口：`GET https://www.hacore.cn/site/learning/series/5`
  —— 只返回 `status = 1` 的已发布文章
- 含草稿的完整目录需带 Token 读取，或直接查本地 `site_db` 的 `learning_chapters` / `learning_articles`

> 当前 84 篇中仅 6 篇已发布（导读 1 + 第 1 章 5），其余为草稿/下架状态。

---

## 四、版本对齐约定（重要）

**问题**：文章写好后代码继续演进，示例就会和正文对不上。

**做法**：

1. **每章一个 git tag**：`ch02`、`ch03`…；章内结构调整用 `ch02.1` 这类小版本
2. **文章里的链接固定到 tag**，不用 `main`：
   ```
   https://github.com/April2144/fullstack-demo-/tree/ch02/frontend/ch02-basics
   ```
3. **文件头标注归属**：
   ```js
   // ===== 对应笔记 2.3 JavaScript 核心语法 =====
   ```
4. **文末统一段落**：
   > 📦 这篇笔记对应的完整工程在 [fullstack-demo](链接)（`ch02` 版本）—— 文件顶部标了对应的笔记编号

**修订流程**：代码改动 → 提交 → 打新 tag（如 `ch02.1`）→ 文章里的链接同步换 tag → `CHANGELOG.md` 记一行。

---

## 五、编写原则

1. **零外部依赖**：前端只用浏览器原生能力；后端只用 Python + FastAPI + SQLite
2. **零配置**：不写死绝对路径、不读环境变量、不连外部数据库
3. **可运行**：每个目录都能单独跑起来，不依赖其它章节
4. **一文件一事**：文件按笔记编号拆分，不把整章塞进一个巨型文件
5. **只写已完成的章节**：未写的章节只留 README 占位，不预造"假代码"

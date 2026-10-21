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

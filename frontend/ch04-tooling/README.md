# 第 4 章 · 前端工程化

对应笔记：`4.1 项目目录结构设计` / `4.2 静态资源管理` / `4.3 代码规范与模块化` / `4.4 构建与压缩` / `4.5 配置管理`

## 文件对照

| 笔记 | 文件 | 内容 |
|---|---|---|
| 4.1 | `01-structure.html` | 四层职责（pages / components / api / utils）、依赖方向、就近原则、三个常见反例 |
| 4.2 | `02-assets.html` | 资源分类、目录约定、版本号与内容哈希、强缓存与失效 |
| 4.3 | `03-modules/index.html` + `03-modules/js/*` | ES Module 四种导入写法、必须走 HTTP、模块作用域 |
| 4.4 | `04-build/04-build.html` + `04-build/build.mjs` + `04-build/src/*` | 零依赖构建：合并、去注释、压空白，实测 2.44 KB → 1.27 KB（-47.8%） |
| 4.5 | `05-config/05-env.html` + `05-config/config.js` + `05-config/env.js` | 一套配置三种环境、环境判定优先级、现场切换、密钥不能放前端 |
| 汇总 | `index.html` | 五节入口页 |

## 怎么跑

```bash
cd frontend/ch04-tooling
python3 -m http.server 8082
# 打开 http://localhost:8082
```

- **4.3 必须走 HTTP**：`import` / `type="module"` 在 `file://` 下会被 CORS 拦掉
- **4.4 先构建**：`cd 04-build && node build.mjs`，否则页面上那行 demo 只会显示提示语
- 4.5 支持 `05-env.html?env=production` 直接指定初始环境

## 说明

- `style.css` 以第 2 章样式为基线复制后追加，保证本章能**单独运行**（代价是部分样式与第 2 章重复）
- `04-build/build.mjs` 只用 Node 内置模块（`node:fs` / `node:path` / `node:url`），**无需 npm install**
- 压缩只做「去注释 + 压行内空白 + 删空行」，**保留换行**：删换行会触发自动分号插入（ASI），改变语义
- `04-build/src/` 里 `utils.js` 必须排在 `app.js` 之前合并，因为 `app.js` 依赖 `formatSize()`
- `dist/` 是构建产物：克隆下来先 `node build.mjs`，不要手改产物
- 4.5 的 `config.js` 只放公开值（接口地址、超时、开关）；**任何密钥都不属于前端配置**
- 全程无框架、无 npm 依赖、无 CDN 依赖

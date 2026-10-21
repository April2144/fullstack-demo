# 第 6 章 · 数据库设计与操作

对应笔记：`6.1 关系型数据库基础` / `6.2 表设计与字段类型` / `6.3 SQL 增删改查` / `6.4 Python 操作 MySQL` / `6.5 数据库连接与配置管理`

## 文件对照

| 笔记 | 文件 | 内容 |
|---|---|---|
| 6.1 | 本文件第一节 | 表 / 行 / 列、主键、外键、索引、关系的三种类型 |
| 6.2 | `schema.mysql.sql`、`schema.sqlite.sql` | 四张表：`users` / `notes` / `tags` / `note_tags`，含主键、外键、唯一索引、联合索引 |
| 6.3 | `queries.sql`、`seed.sql` | 增删改查、多表 JOIN、聚合 + HAVING、子查询、分页 |
| 6.4 | `crud_demo.py` | 命令行跑一轮 CRUD，含事务失败回滚、LEFT JOIN、先查后删 |
| 6.5 | `db.py`、`db_config.example.json` | 连接工厂、配置分层、事务上下文、两种后端的差异收口 |

## 怎么跑

```bash
cd backend/ch06-database

# 方式一：零配置，用 SQLite（克隆下来就能跑）
python3 crud_demo.py

# 反复演示时重建演示库
python3 crud_demo.py --reset

# 方式二：真实 MySQL（先建库、复制配置）
mysql -uroot -e "CREATE DATABASE fullstack_demo DEFAULT CHARSET utf8mb4;"
cp db_config.example.json db_config.json   # 改成自己的账号密码
python3 crud_demo.py --backend mysql
```

依赖：SQLite 方式只用标准库；MySQL 方式需要 `pip install pymysql`。

预期输出（关键几行）：

```
--- 1. 已发布的笔记，按阅读数倒序 ---
  id=1  title=FastAPI 入门  status=published  view_count=42
--- 4. 事务回滚演示 ---
  捕获到异常：IntegrityError
  事务前后 users 行数：2 → 2（没有多出半条脏数据）
```

## 一、6.1 关系型数据库基础

- **表（table）**：一类数据的集合，`notes` 存笔记、`users` 存用户
- **行（row）**：一条记录；**列（column）**：一个字段，有固定类型
- **主键（primary key）**：唯一标识一行，本目录统一用自增整数
- **外键（foreign key）**：`notes.user_id → users.id`，数据库帮你守住「笔记必须属于一个存在的用户」
- **索引（index）**：为常用查询条件建的目录，换来更快的读、更慢的写

关系的三种类型：

| 关系 | 例子 | 实现方式 |
|---|---|---|
| 一对多 | 一个用户有多篇笔记 | 在「多」的一方加外键（`notes.user_id`） |
| 多对多 | 笔记有多个标签，标签属于多篇笔记 | 中间表 `note_tags`，复合主键 `(note_id, tag_id)` |
| 一对一 | 用户 ↔ 用户资料 | 同一张表，或另一张表用唯一外键 |

## 二、6.2 字段类型怎么选

| 用途 | MySQL | SQLite | 选型要点 |
|---|---|---|---|
| 自增主键 | `INT UNSIGNED AUTO_INCREMENT` | `INTEGER PRIMARY KEY AUTOINCREMENT` | 别用业务字段（手机号、邮箱）当主键 |
| 短文本 | `VARCHAR(32)` | `TEXT` | 长度按真实上限给，不要一律 `VARCHAR(255)` |
| 长文本 | `TEXT` | `TEXT` | 正文类内容 |
| 枚举 | `ENUM('draft','published')` | `TEXT` + `CHECK` | 取值固定且少；会频繁增删的用字典表 |
| 时间 | `DATETIME` | `TEXT`（ISO 字符串） | `updated_at` 交给数据库维护，别信客户端时间 |
| 计数 | `INT UNSIGNED` | `INTEGER` | 无符号能省一半范围浪费，也防止负数 |

**索引怎么建**：`WHERE`、`JOIN ON`、`ORDER BY` 里出现的列才考虑；
本目录建了两个：`idx_notes_user`（按作者查）、`idx_notes_status_created`（按状态筛选再按时间排）。
联合索引要按「等值在前、范围/排序在后」排，`(status, created_at)` 就是按这个顺序来的。

## 三、两种方言的差异（重要）

本目录代码以 **MySQL** 为正文口径，为了让读者零配置就能跑，另附一份 SQLite 版本。
真正会踩到的差异只有这几条：

| 项目 | MySQL | SQLite |
|---|---|---|
| 自增 | `AUTO_INCREMENT` | `AUTOINCREMENT` |
| 占位符 | `%s` | `?` |
| 取新 id | `LAST_INSERT_ID()` | `lastrowid` |
| 外键校验 | InnoDB 默认开启 | **默认关闭**，连接后要 `PRAGMA foreign_keys = ON` |
| 建表附加项 | `ENGINE=InnoDB`、`CHARSET=utf8mb4` | 无 |
| 时间默认值 | `CURRENT_TIMESTAMP` | `datetime('now')`（`CURRENT_TIMESTAMP` 也支持） |

> 这些差异全部收在 `db.py` 的 `connect()` / `placeholder()` / `Database` 里，
> 业务代码写一套 SQL 就能切后端 —— 这也是 6.5「配置管理」要解决的问题。

## 四、几个容易错的点

1. **忘了 `WHERE` 的 `UPDATE` / `DELETE` 是全表操作**：`crud_demo.py` 里删除前先 `SELECT` 预览，就是这个习惯
2. **不要自己拼 SQL 字符串**：一律用占位符 + 参数元组，`f"WHERE id = {user_input}"` 等于把库交给别人
3. **外键不是性能负担，是数据保险**：真要删用户还得留他的笔记，就别用 `ON DELETE CASCADE`
4. **`COUNT(*)` 大表很慢**：分页总数在数据量大时应改用估算或缓存
5. **删除优先考虑软删除**：加 `deleted_at` 列，查询时过滤，误删还有救

## 五、产物说明

- `demo.db` 是 SQLite 方式运行时自动生成的演示库，已在 `.gitignore` 里排除（`*.db`）
- `db_config.json` 含真实密码，**不要提交**；仓库里只保留 `db_config.example.json`

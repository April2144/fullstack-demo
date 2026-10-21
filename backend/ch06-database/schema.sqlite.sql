-- ===== 对应笔记 6.2 表设计与字段类型（SQLite 方言，本目录零配置演示用）=====
-- 与 schema.mysql.sql 结构等价，差别只有方言，见 README「方言对照」一节。

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    username    TEXT         NOT NULL UNIQUE,
    email       TEXT         NOT NULL,
    created_at  TEXT         NOT NULL DEFAULT (datetime('now'))
);

-- 笔记表：user_id 是外键，ON DELETE CASCADE 表示删用户时连带删他的笔记
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    title       TEXT         NOT NULL,
    content     TEXT         NOT NULL,
    status      TEXT         NOT NULL DEFAULT 'draft'
                             CHECK (status IN ('draft', 'published')),
    view_count  INTEGER      NOT NULL DEFAULT 0,
    created_at  TEXT         NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT         NOT NULL DEFAULT (datetime('now'))
);

-- 索引：等值查询多的列单独建，范围 + 排序的组合列建联合索引
CREATE INDEX IF NOT EXISTS idx_notes_user ON notes (user_id);
CREATE INDEX IF NOT EXISTS idx_notes_status_created ON notes (status, created_at);

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL UNIQUE
);

-- 中间表：复合主键保证「同一条笔记 + 同一个标签」只出现一次
CREATE TABLE IF NOT EXISTS note_tags (
    note_id  INTEGER NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
    tag_id   INTEGER NOT NULL REFERENCES tags  (id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_note_tags_tag ON note_tags (tag_id);

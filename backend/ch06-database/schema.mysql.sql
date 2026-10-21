-- ===== 对应笔记 6.2 表设计与字段类型（MySQL 8.0 方言，正文主口径）=====
-- 说明：这份 DDL 用于真实 MySQL；本目录的零配置演示跑的是 schema.sqlite.sql
--      （结构等价，差异见 README 的「方言对照」）

-- 用户表：一个账号一行
CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
    username    VARCHAR(32)     NOT NULL               COMMENT '登录名，唯一',
    email       VARCHAR(120)    NOT NULL               COMMENT '邮箱',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';

-- 笔记表：一篇文章一行，user_id 指向作者
CREATE TABLE IF NOT EXISTS notes (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
    user_id     INT UNSIGNED    NOT NULL               COMMENT '作者，外键指向 users.id',
    title       VARCHAR(120)    NOT NULL               COMMENT '标题',
    content     TEXT            NOT NULL               COMMENT '正文',
    status      ENUM('draft', 'published') NOT NULL DEFAULT 'draft' COMMENT '状态：草稿 / 已发布',
    view_count  INT UNSIGNED    NOT NULL DEFAULT 0     COMMENT '阅读数',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间，由数据库维护',
    PRIMARY KEY (id),
    KEY idx_notes_user (user_id),
    KEY idx_notes_status_created (status, created_at),
    CONSTRAINT fk_notes_user FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '笔记表';

-- 标签表：标签独立成表，一条笔记可以有多个标签
CREATE TABLE IF NOT EXISTS tags (
    id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name  VARCHAR(20)  NOT NULL COMMENT '标签名',
    PRIMARY KEY (id),
    UNIQUE KEY uk_tags_name (name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '标签表';

-- 中间表：多对多关系的标准做法，主键是两列的组合
CREATE TABLE IF NOT EXISTS note_tags (
    note_id  BIGINT UNSIGNED NOT NULL,
    tag_id   INT UNSIGNED    NOT NULL,
    PRIMARY KEY (note_id, tag_id),
    KEY idx_note_tags_tag (tag_id),
    CONSTRAINT fk_note_tags_note FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
    CONSTRAINT fk_note_tags_tag  FOREIGN KEY (tag_id)  REFERENCES tags  (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '笔记-标签关联表';

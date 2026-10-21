-- ===== 对应笔记 6.3 SQL 增删改查：样例数据 =====
-- 显式写 id 是为了让 JOIN 示例的结果可预期；真实项目交给自增主键，
-- 绝不要在前端或业务代码里自己算 id。

INSERT INTO users (id, username, email) VALUES
    (1, 'zhangsan', 'zhangsan@example.com'),
    (2, 'lisi',     'lisi@example.com');

INSERT INTO notes (id, user_id, title, content, status, view_count) VALUES
    (1, 1, 'FastAPI 入门',       '从安装到跑起第一个接口。',   'published', 42),
    (2, 1, 'MySQL 索引笔记',     '什么时候该建索引。',         'published', 18),
    (3, 2, 'Nginx 反向代理配置', '把 80 端口的请求转给 8000。', 'draft',      0);

INSERT INTO tags (id, name) VALUES
    (1, 'backend'),
    (2, 'database');

-- 多对多：笔记 1 和 2 都有 backend 标签，笔记 1 额外有 database
INSERT INTO note_tags (note_id, tag_id) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (3, 1);

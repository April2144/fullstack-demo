-- ===== 对应笔记 6.3 SQL 增删改查 =====
-- 全部语句在 MySQL 8.0 与 SQLite 3 上都能跑（特例已单独标注）。
-- 演示顺序：先查 → 再增 → 改 → 删，因为「先查后删」本身就是必须养成的习惯。

/* ---------- 1. 查：过滤 + 排序 + 分页 ---------- */
-- 已发布的笔记，按阅读数倒序，取前 10 条（第 1 页）
SELECT id, title, view_count
FROM notes
WHERE status = 'published'
ORDER BY view_count DESC
LIMIT 10 OFFSET 0;

-- 标题里带关键字的模糊搜索：% 代表任意字符，注意前置 % 用不上索引
SELECT id, title
FROM notes
WHERE title LIKE '%代理%';

/* ---------- 2. 查：多表 JOIN ---------- */
-- 笔记 + 作者 + 它的标签（一篇笔记有多个标签会变成多行，这是正常的）
SELECT n.id, n.title, u.username, t.name AS tag
FROM notes AS n
         JOIN users AS u ON u.id = n.user_id
         LEFT JOIN note_tags AS nt ON nt.note_id = n.id
         LEFT JOIN tags AS t ON t.id = nt.tag_id
ORDER BY n.id, t.name;

-- LEFT JOIN 与 JOIN 的区别：用 LEFT 才能看到「没有标签」的笔记
SELECT n.id, n.title, COUNT(nt.tag_id) AS tag_count
FROM notes AS n
         LEFT JOIN note_tags AS nt ON nt.note_id = n.id
GROUP BY n.id, n.title;

/* ---------- 3. 查：聚合 + HAVING ---------- */
-- 每个作者发了几篇已发布的笔记；HAVING 过滤的是聚合后的结果
SELECT u.username, COUNT(*) AS note_count, SUM(n.view_count) AS total_views
FROM users AS u
         JOIN notes AS n ON n.user_id = u.id
WHERE n.status = 'published'
GROUP BY u.id, u.username
HAVING COUNT(*) >= 1
ORDER BY total_views DESC;

-- 子查询：阅读数高于全站平均值的笔记
SELECT id, title, view_count
FROM notes
WHERE view_count > (SELECT AVG(view_count) FROM notes);

/* ---------- 4. 增：INSERT ---------- */
INSERT INTO notes (user_id, title, content, status)
VALUES (2, '一条草稿', '这条是 6.3 演示插入的。', 'draft');

-- 取刚插入的自增 id：
--   MySQL：SELECT LAST_INSERT_ID();
--   SQLite：cursor.lastrowid（Python 里直接用，不写 SQL）

/* ---------- 5. 改：UPDATE ---------- */
-- 改之前先查，确认 WHERE 命中的行数对不对 —— 忘了 WHERE 就是全表更新
SELECT id, title FROM notes WHERE status = 'draft';

UPDATE notes
SET status     = 'published',
    view_count = view_count + 1
WHERE id = 4;

/* ---------- 6. 删：DELETE ---------- */
-- 永久删除前先用同样条件的 SELECT 预览
SELECT id, title FROM notes WHERE status = 'draft' AND view_count = 0;

-- 真实项目更常用「软删除」：加一列 deleted_at，删除只是写时间戳
-- UPDATE notes SET deleted_at = CURRENT_TIMESTAMP WHERE id = 4;

# ===== 对应笔记 6.4 Python 操作 MySQL =====
"""
一轮完整的增删改查，每一步都打印结果，方便对照 6.3 的 SQL 语句看。

    python3 crud_demo.py                  # 默认 SQLite，零配置直接跑
    python3 crud_demo.py --backend mysql  # 走真实 MySQL，需要 db_config.json

两种后端共用同一份业务 SQL，只有占位符和驱动不同 —— 差异都收在 db.py 里。
"""

import argparse

import db as database


def show(title, rows):
    """打印查询结果。字段少的时候一行一条比表格更好读，也不担心中文宽度对齐。"""
    print('\n--- %s ---' % title)
    if not rows:
        print('(无数据)')
        return
    for row in rows:
        pairs = ['%s=%s' % (key, value) for key, value in row.items()]
        print('  ' + '  '.join(pairs))


def main():
    parser = argparse.ArgumentParser(description='第 6 章：Python 操作数据库演示')
    parser.add_argument('--backend', choices=['sqlite', 'mysql'],
                        help='默认读 db_config.json，没有配置就用 sqlite')
    parser.add_argument('--reset', action='store_true',
                        help='删除 SQLite 演示库后重建，便于反复演示')
    args = parser.parse_args()

    if args.reset:
        config = database.load_config()
        path = config['sqlite']['path']
        if args.backend != 'mysql' and path != ':memory:':
            import os
            if os.path.exists(path):
                os.remove(path)
                print('已删除旧库：%s' % path)

    with database.Database(args.backend) as db:
        database.ensure_schema(db)
        print('当前后端：%s' % db.backend)
        mark = database.placeholder(db.backend)

        # ---------- 1. 查：带条件 + 排序 ----------
        rows = db.query(
            'SELECT id, title, status, view_count FROM notes '
            'WHERE status = ' + mark + ' ORDER BY view_count DESC',
            ('published',)
        )
        show('1. 已发布的笔记，按阅读数倒序', rows)

        # ---------- 2. 增：插入一条草稿 ----------
        with database.transaction(db):
            new_id = db.insert(
                'INSERT INTO notes (user_id, title, content, status) VALUES (' +
                ', '.join([mark] * 4) + ')',
                (1, 'Python 操作数据库', '这条由 crud_demo.py 插入。', 'draft')
            )
        print('\n--- 2. 插入草稿 ---')
        print('  新笔记 id=%s（自增主键由数据库生成，业务代码不自己算）' % new_id)

        # ---------- 3. 改：发布它 ----------
        with database.transaction(db):
            affected = db.execute(
                'UPDATE notes SET status = ' + mark + ', view_count = view_count + 1 '
                'WHERE id = ' + mark,
                ('published', new_id)
            )
        print('\n--- 3. 发布这条草稿 ---')
        print('  影响行数=%s（应为 1；如果是 0，说明 id 不存在）' % affected)

        # ---------- 4. 事务：失败要整体回滚 ----------
        before = db.query_one('SELECT COUNT(*) AS total FROM users')['total']
        try:
            with database.transaction(db):
                db.insert('INSERT INTO users (username, email) VALUES (' + mark + ', ' + mark + ')',
                          ('zhangsan', 'another@example.com'))  # username 唯一，必定冲突
        except Exception as exc:
            print('\n--- 4. 事务回滚演示 ---')
            print('  捕获到异常：%s' % type(exc).__name__)
        after = db.query_one('SELECT COUNT(*) AS total FROM users')['total']
        print('  事务前后 users 行数：%s → %s（没有多出半条脏数据）' % (before, after))

        # ---------- 5. 关联查询：一篇笔记的标签 ----------
        rows = db.query(
            'SELECT n.id, n.title, t.name AS tag FROM notes AS n '
            'LEFT JOIN note_tags AS nt ON nt.note_id = n.id '
            'LEFT JOIN tags AS t ON t.id = nt.tag_id '
            'ORDER BY n.id, t.name'
        )
        show('5. 笔记 + 标签（LEFT JOIN，没标签的也会出现）', rows)

        # ---------- 6. 删：先查后删 ----------
        preview = db.query('SELECT id, title FROM notes WHERE id = ' + mark, (new_id,))
        show('6. 删除前先确认命中的是哪一行', preview)
        if preview:
            with database.transaction(db):
                db.execute('DELETE FROM notes WHERE id = ' + mark, (new_id,))
            print('  已删除 id=%s' % new_id)

        remain = db.query_one('SELECT COUNT(*) AS total FROM notes')['total']
        print('\n结束：notes 剩余 %s 行（回到演示开始时的数量）' % remain)


if __name__ == '__main__':
    main()

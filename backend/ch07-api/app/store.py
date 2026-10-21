# ===== 数据层（SQLite）=====
"""
只负责读写数据，不出现 Request / Response 这些 HTTP 概念。

和第 5 章的内存 store 相比，区别只有一处：数据落在文件里。
接口层调用方式完全一样（list / get / create / update / delete）。
"""

import contextlib
import datetime
import sqlite3

from app.config import settings
from app.errors import BusinessError

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL DEFAULT '',
    status      TEXT    NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'published')),
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);
"""

SEED = [
    ('FastAPI 接口设计', '从路由、状态码到响应结构。', 'published'),
    ('请求与响应格式', '统一响应包怎么写。', 'published'),
    ('跨域是怎么产生的', '同源策略与 CORS 预检。', 'draft'),
]


def _now():
    """统一时间格式：ISO 8601，前端 new Date() 可直接解析。"""
    return datetime.datetime.now().isoformat(timespec='seconds')


class NoteStore:
    def __init__(self, db_path=None):
        self.db_path = db_path or settings.db_path

    def connect(self):
        """每次操作开一个连接：同步路由跑在线程池里，跨线程复用连接会报错。"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextlib.contextmanager
    def connection(self):
        """开连接 → 正常提交 / 异常回滚 → 一定关闭。

        注意：sqlite3 自带的 `with conn` 只管提交，不负责关闭，
        写成 `with self.connect() as conn` 会漏连接。
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """建表 + 空库时插入样例。启动钩子里调用一次。"""
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            total = conn.execute('SELECT COUNT(*) AS total FROM notes').fetchone()['total']
            if total == 0:
                now = _now()
                conn.executemany(
                    'INSERT INTO notes (title, content, status, created_at, updated_at) '
                    'VALUES (?, ?, ?, ?, ?)',
                    [(title, content, status, now, now) for title, content, status in SEED]
                )

    # ---------- 读 ----------
    def list(self, limit, offset, status=None):
        """返回 (当页数据, 总数)。总数和当页长度是两件事。"""
        where = ''
        params = []
        if status:
            where = ' WHERE status = ?'
            params.append(status)

        with self.connection() as conn:
            total = conn.execute('SELECT COUNT(*) AS total FROM notes' + where, params).fetchone()['total']
            rows = conn.execute(
                'SELECT * FROM notes' + where + ' ORDER BY id DESC LIMIT ? OFFSET ?',
                params + [limit, offset]
            ).fetchall()

        return [dict(row) for row in rows], total

    def get(self, note_id):
        with self.connection() as conn:
            row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
        if row is None:
            # 数据层直接抛业务错误，路由层就不用写 if not note 了
            raise BusinessError(f'笔记 {note_id} 不存在', code=404)
        return dict(row)

    # ---------- 写 ----------
    def create(self, title, content, status):
        now = _now()
        with self.connection() as conn:
            cursor = conn.execute(
                'INSERT INTO notes (title, content, status, created_at, updated_at) '
                'VALUES (?, ?, ?, ?, ?)',
                (title, content, status, now, now)
            )
            row = conn.execute('SELECT * FROM notes WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return dict(row)

    def update(self, note_id, fields):
        """只更新传进来的字段。字段名来自白名单，不拼接用户输入。"""
        allowed = [key for key in ('title', 'content', 'status') if key in fields]
        if not allowed:
            return self.get(note_id)

        assignments = ', '.join(['%s = ?' % key for key in allowed])
        params = [fields[key] for key in allowed] + [_now(), note_id]

        with self.connection() as conn:
            affected = conn.execute(
                'UPDATE notes SET %s, updated_at = ? WHERE id = ?' % assignments, params
            ).rowcount
            if affected == 0:
                raise BusinessError(f'笔记 {note_id} 不存在', code=404)
            row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
        return dict(row)

    def delete(self, note_id):
        with self.connection() as conn:
            affected = conn.execute('DELETE FROM notes WHERE id = ?', (note_id,)).rowcount
        if affected == 0:
            raise BusinessError(f'笔记 {note_id} 不存在', code=404)


# 单例：路由通过 deps.get_store() 拿到它
note_store = NoteStore()

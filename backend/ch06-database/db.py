# ===== 对应笔记 6.5 数据库连接与配置管理 =====
"""
连接与配置集中在这一个文件，业务代码只认 Database。

设计要点：
  1. 配置分三层：显式传参 > db_config.json > 内置默认值（SQLite）
  2. 没有 db_config.json 也能跑 —— 默认用本目录的 demo.db，零配置
  3. 不在模块顶层建立连接：那会导致「导入即连接」，测试和多进程场景都会出问题
  4. 两种后端的差异（占位符、游标、返回类型）全部收在这里，不泄漏给业务代码
"""

import os
import json
import sqlite3
import contextlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'db_config.json')
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, 'demo.db')

# 内置默认值：SQLite + 本地文件，克隆下来就能跑
DEFAULT_CONFIG = {
    'backend': 'sqlite',
    'sqlite': {
        'path': DEFAULT_SQLITE_PATH
    },
    'mysql': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': 'fullstack_demo',
        'charset': 'utf8mb4'
    }
}


def load_config(path=None):
    """读配置；文件不存在就用内置默认值。

    合并策略是「按层覆盖」：db_config.json 里只写想改的项，
    没写的自动沿用默认值，避免以后加字段要求所有人改配置。
    """
    path = path or CONFIG_PATH
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if not os.path.exists(path):
        return config

    with open(path, 'r', encoding='utf-8') as fp:
        user_config = json.load(fp)

    for key, value in user_config.items():
        if isinstance(value, dict):
            config.setdefault(key, {}).update(value)
        else:
            config[key] = value
    return config


def placeholder(backend):
    """参数化占位符：SQLite 是 ?，MySQL 是 %s。

    占位符必须交给驱动去拼，绝不能自己写 f-string —— 那是 SQL 注入的入口。
    """
    return '%s' if backend == 'mysql' else '?'


def connect(backend=None, config=None):
    """建立一个底层连接。日常业务请用 Database，它负责关闭与类型转换。"""
    config = config or load_config()
    backend = backend or config.get('backend', 'sqlite')

    if backend == 'mysql':
        try:
            import pymysql
        except ImportError:
            raise SystemExit('未安装 pymysql：pip install pymysql（或去掉 --backend mysql，用默认的 SQLite）')

        settings = config['mysql']
        return pymysql.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['database'],
            charset=settings.get('charset', 'utf8mb4'),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False  # 显式提交：事务边界由业务决定
        )

    # SQLite：文件不存在会自动创建；传 ':memory:' 可用于测试
    conn = sqlite3.connect(config['sqlite']['path'])
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')  # SQLite 默认不校验外键，必须手动打开
    return conn


class Database:
    """薄封装：把「两种后端写法不同」的地方收口成 query / execute。"""

    def __init__(self, backend=None, config=None):
        self.config = config or load_config()
        self.backend = backend or self.config.get('backend', 'sqlite')

        # 指定了 MySQL 却没有配置文件时，先给明确指引：
        # 否则会拿着默认的 root/空密码去连，报出「Unknown database」这种与真实原因无关的错
        if self.backend == 'mysql' and not os.path.exists(CONFIG_PATH):
            raise SystemExit(
                '缺少 db_config.json：先执行\n'
                '  cp db_config.example.json db_config.json\n'
                '再改成自己的 host / user / password / database'
            )

        self.conn = connect(self.backend, self.config)

    # ---- 查询 ----
    def query(self, sql, params=()):
        """返回 list[dict]；没有数据就是空列表，不返回 None。"""
        if self.backend == 'mysql':
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                return list(cursor.fetchall())
        rows = self.conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def query_one(self, sql, params=()):
        """返回一条 dict；查不到返回 None。"""
        if self.backend == 'mysql':
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        row = self.conn.execute(sql, params).fetchone()
        return dict(row) if row is not None else None

    # ---- 写入 ----
    def execute(self, sql, params=()):
        """执行一条写语句，返回影响行数（不提交，提交交给事务）。"""
        if self.backend == 'mysql':
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount
        return self.conn.execute(sql, params).rowcount

    def insert(self, sql, params=()):
        """插入并返回新行 id。"""
        if self.backend == 'mysql':
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.lastrowid
        return self.conn.execute(sql, params).lastrowid

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # 出异常时回滚，正常退出不自动提交 —— 提交由业务显式控制
        if exc_type is not None:
            self.conn.rollback()
        self.close()
        return False


@contextlib.contextmanager
def transaction(db):
    """事务上下文：正常退出提交，抛异常整体回滚。

    with transaction(db):
        db.execute(...)          # 多条写操作要么全成，要么全不成
        db.execute(...)
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def _split_statements(sql):
    """按分号切语句，并丢掉整行注释。

    够用的最小实现；真正的迁移工具会正经解析语法。
    字符串里含分号时这个切法会出错，所以只用于本目录的示例脚本。
    """
    kept = [line for line in sql.splitlines() if not line.strip().startswith('--')]
    return [part.strip() for part in '\n'.join(kept).split(';') if part.strip()]


def execute_script(db, sql_path):
    """整份 SQL 文件执行一遍（建表 / 灌样例数据用）。"""
    with open(sql_path, 'r', encoding='utf-8') as fp:
        statements = _split_statements(fp.read())

    if db.backend == 'mysql':
        with db.conn.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        db.commit()
        return

    db.conn.executescript(';\n'.join(statements))


def ensure_schema(db):
    """建表 + 空库时灌样例数据。重复执行安全（IF NOT EXISTS + 计数判断）。"""
    schema_file = 'schema.mysql.sql' if db.backend == 'mysql' else 'schema.sqlite.sql'
    execute_script(db, os.path.join(BASE_DIR, schema_file))

    row = db.query_one('SELECT COUNT(*) AS total FROM users')
    if row is None or row['total'] == 0:
        execute_script(db, os.path.join(BASE_DIR, 'seed.sql'))

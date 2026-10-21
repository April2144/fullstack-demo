# ===== 对应笔记 5.4 / 5.6：数据层（内存版）=====
"""
第 5 章还不讲数据库，所以用一个内存仓库把「数据怎么存」这件事挡住。

它同时展示了依赖注入的价值：
  路由只要说「给我一个 store」，不关心它是内存、SQLite 还是 MySQL。
  第 6、7 章换成真数据库时，路由代码一行都不用改。
"""

import threading

from app.errors import BusinessError


class ItemStore:
    def __init__(self):
        # 同步路由跑在线程池里，多个请求可能同时改字典，加锁最稳
        self._lock = threading.Lock()
        self._items = {
            1: {'id': 1, 'name': '机械键盘', 'price': 399.0, 'tags': ['硬件']},
            2: {'id': 2, 'name': '显示器支架', 'price': 159.0, 'tags': ['硬件']},
            3: {'id': 3, 'name': 'Python 教程', 'price': 0.0, 'tags': ['书', '电子']},
        }
        self._next_id = 4

    def list(self, limit, offset, keyword=None):
        """返回 (当页数据, 满足条件的总数)。总数和当页长度是两件事，别混。"""
        rows = list(self._items.values())

        if keyword:
            # 简单的大小写无关包含匹配；真实项目用数据库的 LIKE / 全文索引
            lowered = keyword.lower()
            rows = [row for row in rows if lowered in row['name'].lower()]

        rows.sort(key=lambda row: row['id'])
        total = len(rows)
        return rows[offset:offset + limit], total

    def get(self, item_id):
        """查不到就抛业务错误，让接口层不用写 if not found。"""
        item = self._items.get(item_id)
        if item is None:
            raise BusinessError(f'商品 {item_id} 不存在', code=404)
        return item

    def create(self, name, price, tags):
        with self._lock:
            item = {'id': self._next_id, 'name': name, 'price': price, 'tags': list(tags)}
            self._items[item['id']] = item
            self._next_id += 1
        return item

    def update(self, item_id, fields):
        """只更新传进来的字段 —— 与 schemas.ItemUpdate 的「全部可选」对应。"""
        with self._lock:
            item = self.get(item_id)
            for key in ('name', 'price', 'tags'):
                if key in fields:
                    item[key] = fields[key]
        return item

    def delete(self, item_id):
        with self._lock:
            self.get(item_id)  # 不存在时抛 404
            del self._items[item_id]


# 单例：整个进程共用一份数据（--reload 时进程重启，数据回到初始状态）
item_store = ItemStore()

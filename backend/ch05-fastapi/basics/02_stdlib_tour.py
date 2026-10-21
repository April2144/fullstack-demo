# ===== 对应笔记 5.1 Python 基础：标准库常用部分 =====
"""
运行：python3 02_stdlib_tour.py

后端写得顺不顺，很大程度取决于「知道标准库已经有什么」。
这几块是第 6、7 章真正会用到的，全部零安装。
"""

import json
import re
import datetime
import tempfile
from collections import Counter
from pathlib import Path


def section(title):
    print('\n' + '-' * 6 + ' ' + title + ' ' + '-' * 6)


# ---------- 1. json：接口的通用语言 ----------
section('1. json')
note = {'id': 1, 'title': '接口返回什么', 'tags': ['api', 'json']}

# ensure_ascii=False 才会保留中文；indent 让日志里的 JSON 可读
text = json.dumps(note, ensure_ascii=False, indent=2)
print(text)

# 反序列化：接口收到的请求体最终都会走这一步
print('解析回来:', json.loads(text)['title'])
print('容错读取:', json.loads('{}').get('title', '默认值'))


# ---------- 2. datetime：时间统一用 ISO 8601 ----------
section('2. datetime')
now = datetime.datetime.now()
print('当前:', now.isoformat(timespec='seconds'))       # 接口里返回这个格式
print('毫秒:', now.isoformat(timespec='milliseconds'))

one_day = datetime.timedelta(days=1)
print('明天此时:', (now + one_day).strftime('%Y-%m-%d %H:%M:%S'))

# 时区：服务器时区设错，日志时间就全乱，排障会多花一倍时间
utc = datetime.datetime.now(datetime.timezone.utc)
print('UTC:', utc.isoformat(timespec='seconds'))


# ---------- 3. pathlib：路径操作不要手拼字符串 ----------
section('3. pathlib')
base = Path(__file__).resolve().parent
print('当前文件所在目录:', base)
print('父目录:', base.parent.name)

# 临时文件：写测试时常用，进程退出自动删除
with tempfile.NamedTemporaryFile('w+', suffix='.txt', encoding='utf-8', delete=True) as fp:
    fp.write('临时内容')
    fp.seek(0)
    print('临时文件读取:', fp.read())


# ---------- 4. re：正则只用来做「匹配 + 提取」 ----------
section('4. re')
email = 'zhangsan@example.com'
pattern = r'^[\w.+-]+@[\w-]+\.[\w.]+$'
print('邮箱格式:', bool(re.match(pattern, email)))

# 用命名分组提取，比按下标取更不容易错
log_line = 'GET /api/notes 200 12.3ms'
match = re.match(r'(?P<method>[A-Z]+) (?P<path>\S+) (?P<status>\d{3})', log_line)
if match:
    print('解析日志:', match.groupdict())


# ---------- 5. Counter：统计频次一行搞定 ----------
section('5. Counter')
statuses = ['published', 'draft', 'published', 'published', 'draft']
print('状态分布:', Counter(statuses))
print('最常见的 1 个:', Counter(statuses).most_common(1))


# ---------- 6. 字符串与数字的边界情况 ----------
section('6. 边界处理')
raw = '  42  '
print('strip + int:', int(raw.strip()))

# 空字符串、None、0 在布尔判断里都是假，但含义完全不同
for value in [0, '', None, [], '0']:
    print(f'  值 {value!r:6} 真假: {bool(value)}')

print('\n提示：接口里要把「没有值」和「值为 0 / 空串」区分开，'
      '所以判断 None 要用 `is None`，不要用 `if not value`。')

# ===== 对应笔记 5.1 Python 基础 =====
"""
直接运行看输出：python3 01_python_basics.py

只讲写 FastAPI 真正会用到的部分，不铺语法大全。
每段都对应后端代码里的一种常见写法。
"""

from dataclasses import dataclass, field


def section(title):
    print('\n' + '-' * 6 + ' ' + title + ' ' + '-' * 6)


# ---------- 1. 变量与类型标注 ----------
section('1. 变量与类型标注')
# Python 是动态类型，但「标注」能让编辑器和 FastAPI 知道你要什么类型
name: str = '张三'
age: int = 28
rate: float = 0.85
is_active: bool = True
print(name, age, rate, is_active)

# f-string：拼接字符串的默认写法，比 + 和 % 都清楚
print(f'{name} 今年 {age} 岁，折扣 {rate:.0%}')

# 类型标注不影响运行（写错了也照跑），但 FastAPI 会用它做请求校验 —— 这是关键
wrong: int = '这行不会报错，但类型标注是假的'


# ---------- 2. 列表、字典、集合 ----------
section('2. 容器')
tags = ['backend', 'python', 'database']
user = {'username': 'zhangsan', 'email': 'zhangsan@example.com'}
unique = {1, 2, 2, 3}  # 集合自动去重

print('列表:', tags, '长度:', len(tags))
print('字典取值:', user['username'], '| get 不会报错:', user.get('phone', '未填'))
print('集合去重:', unique)

# 切片：左闭右开，最常用于分页
print('前两条:', tags[:2], '| 从第 2 条开始:', tags[1:])
print('反转:', tags[::-1])


# ---------- 3. 推导式 ----------
section('3. 推导式')
# 列表推导：把「循环 + 追加」压成一行
upper = [t.upper() for t in tags]
print('转大写:', upper)

# 带条件：只保留长度大于 6 的
long_tags = [t for t in tags if len(t) > 6]
print('长度 > 6:', long_tags)

# 字典推导：常用于「列表转字典」加速查找
by_name = {t: len(t) for t in tags}
print('名字→长度:', by_name)


# ---------- 4. 函数：默认参数与关键字参数 ----------
section('4. 函数')
def paginate(items, limit=10, offset=0):
    """默认参数只在函数定义时求值一次，所以别用可变对象（list/dict）当默认值。"""
    return items[offset:offset + limit]

print('默认:', paginate(tags))
print('关键字参数:', paginate(tags, limit=1, offset=1))
print('只传要改的:', paginate(tags, offset=2))

# 陷阱演示：默认值是列表会跨调用累积
def bad_append(item, bucket=[]):  # 反例，别这么写
    bucket.append(item)
    return bucket

print('反例第一次:', bad_append('a'))
print('反例第二次:', bad_append('b'), '<- 上一次的结果还在')


# ---------- 5. 类与 dataclass ----------
section('5. 类与 dataclass')
class Note:
    """普通类：要自己写 __init__ 和 __repr__。"""

    def __init__(self, title, status='draft'):
        self.title = title
        self.status = status


@dataclass
class NoteDC:
    """dataclass 自动生成 __init__ / __repr__ / __eq__，写数据载体最省事。"""
    title: str
    status: str = 'draft'
    tags: list = field(default_factory=list)  # 可变默认值必须用 factory


print(Note('普通类'))
print(NoteDC('dataclass 版', tags=['python']))


# ---------- 6. 异常处理 ----------
section('6. 异常')
def parse_age(raw):
    """后端所有外部输入都可能是脏的，函数要给出明确失败方式。"""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        # 不要写 except: —— 那会连 Ctrl+C 一起吞掉
        print(f'  无法解析: {raw!r}')
        return None
    else:
        print(f'  解析成功: {value}')
        return value
    finally:
        # 无论成功失败都执行，适合放关闭文件、释放连接
        pass

parse_age('28')
parse_age('二十八')


# ---------- 7. 模块与入口守卫 ----------
section('7. __main__')
print('当前模块名:', __name__)
print('被 import 时 __name__ 是文件名，直接运行时是 "__main__"')
print('所以脚本末尾要写 if __name__ == "__main__":，见文件底部')
print(f'（故意留一个未使用的变量演示标注不校验：{wrong}）')


if __name__ == '__main__':
    # 只有直接运行本文件时才走这里；被别的模块 import 时不执行
    print('\n主流程结束')

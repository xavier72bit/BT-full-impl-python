# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : task_queue.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 13:33

# std import
import queue
import functools


class TaskQueue:
    def __init__(self):
        self.q = queue.Queue()

    def put(self, func, *args, **kwargs):
        # 绑定函数和参数，打包成一个可调用对象
        task = functools.partial(func, *args, **kwargs)
        self.q.put(task)

    def get(self):
        return self.q.get()

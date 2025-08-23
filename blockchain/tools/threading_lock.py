# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : threading_lock.py.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 10:10
# 用类实现锁的功能,实例化一个类就是一个锁,这样可以区分粒度,另外通过装饰器的方式为方法的执行加锁

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable

# std import
import threading
import functools


__all__ = ['Lock']


class Lock:
    def __init__(self):
        self.__lock = threading.RLock()

    def func_lock(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.__lock:
                return func(*args, **kwargs)
        return wrapper

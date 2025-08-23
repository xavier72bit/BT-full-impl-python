# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : worker.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 13:20

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.node_types import TaskQueue


class Worker:
    def __init__(self, tq: TaskQueue):
        self.tq = tq

    def run(self):
        while True:
            task = self.tq.get()
            try:
                task()
            except Exception as e:
                print(f"任务执行失败 {e}")

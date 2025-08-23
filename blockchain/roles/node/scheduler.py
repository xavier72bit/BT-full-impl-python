# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : scheduler.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 12:00

# 3rd import
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


__all__ = ['Scheduler']


class Scheduler:
    """
    调度器, 用于定时执行
    """
    def __init__(self):
        self._scheduler = BackgroundScheduler()

    def add_interval_job(self, func, minutes=0, seconds=0, job_name=None):
        job_name = job_name or func.__name__

        self._scheduler.add_job(
            func,
            trigger=IntervalTrigger(minutes=minutes, seconds=seconds),
            id=job_name,
            max_instances=1,    # 避免重叠
            replace_existing=True,
        )

    def start(self):
        self._scheduler.start()

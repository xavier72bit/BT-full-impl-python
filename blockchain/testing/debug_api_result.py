# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : debug_api_result.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 13:01

from dataclasses import dataclass, asdict

@dataclass
class Result:
    success: bool
    message: str

    def serialize(self):
        return asdict(self)

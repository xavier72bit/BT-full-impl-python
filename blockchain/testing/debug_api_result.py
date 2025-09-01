# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : debug_api_result.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 13:01

from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class Result:
    success: bool
    message: str
    data: Any

    def serialize(self):
        return asdict(self)

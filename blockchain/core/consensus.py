# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : consensus.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 10:27
# 共识机制

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node

class POWConsensus:
    def __init__(self, node: None):
        self.node = node

    def need_update(self, summary):
        pass
# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : consensus.py
# @Author : Xavier Wu
# @Date   : 2025/8/23 10:27
# 共识机制

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node
    from ..types.core_types import BlockChainSummary

# 3rd import
from loguru import logger

class POWConsensus:
    def __init__(self, node: Node):
        self.node = node

    def execute_consensus(self, bc_data):
        """
        执行共识
        """
        pass

    def check_summary(self, bc_summary: BlockChainSummary):
        logger.info(f"共识检查: {bc_summary.serialize()}")

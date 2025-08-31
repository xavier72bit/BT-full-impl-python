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
    from ..types.network_types import NetworkNodePeer

# 3rd import
from loguru import logger

# local import
from .block import Block


class POWConsensus:
    def __init__(self, node: Node):
        self.node = node

    def execute_consensus(self, bc_data: dict):
        """
        执行共识机制算法, 将更权威的链的区块数据补充到自己的链上, 并将拆除的区块内的所有交易信息重新放回交易池中
        """
        #TODO
        logger.info("执行共识算法")

    def check_summary(self, bc_summary: BlockChainSummary, src_peer: NetworkNodePeer) -> bool:
        current_summary = self.node.blockchain.summary

        if (bc_summary.total_difficulty > current_summary.total_difficulty
                and bc_summary.total_length > bc_summary.total_length):
            logger.info("检测到BlockChain Summary的难度与长度均大于本机BlockChain数据, 创建执行共识算法的Task")
            return True
        else:
            logger.info("本机BlockChain数据更加权威, 跳过共识机制算法")
            return False

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
    from ..types.role_types import Node
    from ..types.core_types import BlockChainSummary, BlockChain
    from ..types.network_types import NetworkNodePeer

# 3rd import
from loguru import logger

# local import
from .block import Block


class POWConsensus:
    def __init__(self, node: Node):
        self.node = node

    def execute_consensus(self, peer_blockchain_data: list[Block]):
        """
        执行共识机制算法, 将更权威的链的区块数据补充到自己的链上, 并将拆除的区块内的所有交易信息重新放回交易池中
        """
        logger.info("共识机制开始执行")
        current_blockchain: BlockChain = self.node.blockchain
        fork_print = self._find_fork_point(peer_blockchain_data)

        # 分叉拆除
        blocks_to_remove = current_blockchain[(fork_print + 1):]
        if blocks_to_remove:
            logger.info(f"需要拆除区块为: {[b.hash for b in blocks_to_remove]}")
            # 将分叉点以后的所有交易信息放回交易池
            for b in blocks_to_remove:
                for tx in b.transactions:
                    self.node.txpool.add_transaction(tx)
            # 回滚到分叉点
            del current_blockchain[(fork_print + 1):]
        else:
            logger.info("没有需要拆除的区块")

        # 新链补充
        blocks_to_add = peer_blockchain_data[(fork_print + 1):]
        for block in blocks_to_add:
            logger.info(f"来自共识机制的区块: {block.hash} 需要上链")
            if block.prev_hash is None:
                block.mark_genesis()
            block.mark_from_peer()
            current_blockchain.add_block(block)

    def _find_fork_point(self, peer_blockchain_data: list[Block]) -> int:
        """
        找到区块链的彼此分叉点
        """
        current_blockchain = self.node.blockchain

        fork_point_index = -1
        for i in range(min(len(current_blockchain), len(peer_blockchain_data))):
            if current_blockchain[i].hash != peer_blockchain_data[i].hash:
                fork_point_index = i - 1
                break

        if fork_point_index == -1:
            fork_point_index = min(len(current_blockchain), len(peer_blockchain_data)) - 1

        return fork_point_index

    def _get_peer_blockchain(self, peer: NetworkNodePeer) -> list[Block]:
        blockchain_data_dict = self.node.peer_client.request_block_chain_data(peer)

        blockchain_data = []
        for bd in blockchain_data_dict:
            b = Block.deserialize(bd)
            if b.prev_hash is None:
                b.mark_genesis()
            blockchain_data.append(b)

        return blockchain_data

    def check_summary(self, bc_summary: BlockChainSummary) -> bool:
        current_summary = self.node.blockchain.summary
        return bc_summary.total_difficulty > current_summary.total_difficulty and bc_summary.total_length > current_summary.total_length

    def run(self, bc_summary: BlockChainSummary, peer: NetworkNodePeer):
        if self.check_summary(bc_summary):
            logger.info("检测到BlockChain Summary的难度与长度均大于本机BlockChain数据, 创建执行共识算法的Task")
            self.execute_consensus(self._get_peer_blockchain(peer))
        else:
            logger.info("本机BlockChain数据更加权威, 跳过共识机制算法")

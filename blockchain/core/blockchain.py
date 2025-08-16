# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node
    from ..types.core_types import Block

# std import
import json


class BlockChain:
    def __init__(self, current_node: Node):
        self.current_node = current_node

        # core
        self.__chain: list[Block] = []

    def __len__(self):
        return len(self.__chain)

    @property
    def pow_difficulty(self) -> int:
        return 4

    @property
    def pow_reward(self) -> int:
        return 1

    @property
    def last_block(self) -> Block | None:
        try:
            b = self.__chain[-1]
        except IndexError:
            return None
        else:
            return b

    @property
    def pow_check(self) -> str:
        return "0" * self.pow_difficulty

    def add_block(self, block: Block | None) -> bool:
        """

        :return: bool
        """
        if block is None:
            return False

        current_txpool = self.current_node.txpool

        if self.valid_new_block(block):
            self.__chain.append(block)
            current_txpool.mark_tx(block)
            return True
        else:
            return False

    def compute_balance(self, wallet_addr) -> int:
        balance = 0
        for b in self.__chain:
            for tx in b.transactions:
                if tx.saddr == wallet_addr:
                    balance -= tx.amount
                elif tx.raddr == wallet_addr:
                    balance += tx.amount
                else:
                    continue
        print(f"计算{wallet_addr}的余额: {balance}")
        return balance

    def valid_proof_of_work(self, block: Block) -> bool:
        return block.hash.startswith(self.pow_check)

    def valid_block_transactions(self, block: Block) -> bool:
        if not block.transactions:
            return False

        # 创世区块暂不检查交易信息
        if block.index == 1:
            return True

        reward_tx_num = 0
        for tx in block.transactions:
            if tx.saddr is None:
                reward_tx_num += 1

            if not tx.verify_sign():
                return False

        if reward_tx_num != 1:
            return False

        return True

    def valid_new_block(self, block: Block) -> bool:
        """
        1. 验证Proof of Work的有效性
        2. 验证hash
        3. 验证block数据

        :param block:
        :return: bool
        """
        # TODO: hash check应该校验
        lb = self.last_block

        pow_check: bool = self.valid_proof_of_work(block)
        tx_check: bool = self.valid_block_transactions(block)

        if lb:
            index_check: bool = lb.index == block.index - 1 and block.index == len(self) + 1
            hash_check: bool = lb.hash == block.prev_hash
            print(f"验证区块: index: {index_check}, hash: {hash_check}, pow: {pow_check}, tx: {tx_check}")
            return all([pow_check, hash_check, index_check, tx_check])
        else:
            index_check: bool = block.index == 1
            print(f"验证区块: index: {index_check}, pow: {pow_check}, tx: {tx_check}")
            return all([pow_check, index_check, tx_check])

    def to_json(self) -> str:
        return json.dumps([b.serialize() for b in self.__chain], sort_keys=True)

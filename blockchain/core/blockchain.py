# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node, TaskQueue
    from ..types.core_types import Block
    from ..types.network_types import PeerClient

# local import
from ..tools.threading_lock import Lock


bcl = Lock()


class BlockChain:
    def __init__(self, current_node: Node):
        self.current_node = current_node
        self.tq: TaskQueue = self.current_node.task_queue
        self.peer_client: PeerClient = self.current_node.peer_client

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
        """
        区块的hash值应当以此值开头
        """
        return "0" * self.pow_difficulty

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

    def valid_block_difficulty(self, block: Block) -> bool:
        return block.difficulty == self.pow_difficulty

    def valid_block_hash(self, block: Block) -> bool:
        block_hash = block.compute_hash()
        return block.hash == block_hash

    def valid_new_block(self, block: Block) -> bool:
        """
        1. 验证Proof of Work的有效性
        2. 验证hash
        3. 验证block数据
        4. 验证difficulty

        :param block:
        :return: bool
        """
        lb = self.last_block

        pow_check: bool = self.valid_proof_of_work(block)
        tx_check: bool = self.valid_block_transactions(block)
        hash_check: bool = self.valid_block_hash(block)

        if lb:
            index_check: bool = lb.index == block.index - 1 and block.index == len(self) + 1
            prev_hash_check: bool = lb.hash == block.prev_hash
            return all([pow_check, hash_check, index_check, tx_check, prev_hash_check])
        else:
            index_check: bool = block.index == 1
            return all([pow_check, index_check, tx_check, hash_check])

    @bcl.func_lock
    def add_block(self, block: Block | None) -> bool:
        """

        :return: bool
        """
        current_txpool = self.current_node.txpool

        # block type check
        if block is None:
            return False

        # block validation check
        if not self.valid_new_block(block):
            return False

        # add block & mark tx verified
        # TODO: 这里应该做一下延迟处理，添加了一个块之后，将第n个之前的块内的所有交易标记为“已确认”
        self.__chain.append(block)
        current_txpool.mark_tx(block)

        # 广播区块
        if not block.is_from_peer:
            self.tq.put(self.peer_client.broadcast_block, block)
        return True

    def serialize(self) -> list[dict]:
        return [b.serialize() for b in self.__chain]

    def serialize_summary(self) -> dict:
        """
        区块链的摘要, 结构如下
        {
            'total_difficulty': xxxx,
            'total_length': xxx,
            'blocks': [
                {'hash': 'xxxx', 'prev_hash': 'xxx'},
                {'hash': 'xxxx', 'prev_hash': 'xxxx'}
            ]
        }
        """
        summary = {
            'total_difficulty': 0,
            'total_length': len(self.__chain),
            'blocks': []
        }

        for block in self.__chain:
            summary['total_difficulty'] += block.difficulty
            summary['blocks'].append({
                'hash': block.hash,
                'prev_hash': block.prev_hash
            })

        return summary

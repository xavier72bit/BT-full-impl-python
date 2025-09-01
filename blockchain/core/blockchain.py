# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.role_types import Node, TaskQueue
    from ..types.core_types import Block
    from ..types.network_types import PeerClient

# std import
from functools import reduce

# 3rd import
from loguru import logger

# local import
from ..tools.threading_lock import Lock
from .block import BlockSummary
from .execute_result import ExecuteResult, ExecuteResultErrorTypes


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

    def __iter__(self):
        return self.__chain.__iter__()

    @property
    def pow_difficulty(self) -> int:
        return 4

    @property
    def pow_reward(self) -> int:
        """
        挖矿奖励
        """
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

    @property
    def summary(self) -> "BlockChainSummary":
        return BlockChainSummary(self)

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
        logger.info(f"计算<addr: {wallet_addr}> 的余额: balance")
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

    def valid_new_block(self, block: Block) -> ExecuteResult:
        """
        1. 验证Proof of Work的有效性
        2. 验证hash
        3. 验证block数据
        4. 验证difficulty

        :param block:
        :return: bool
        """
        if not self.valid_block_hash(block):
            msg = f"区块的hash数据验证失败"
            logger.error(msg)
            return ExecuteResult(False, ExecuteResultErrorTypes.BLK_INVALID_HASH, msg)

        if not self.valid_proof_of_work(block):
            msg = f"区块的pow数据验证失败"
            logger.error(msg)
            return ExecuteResult(False, ExecuteResultErrorTypes.BLK_INVALID_POW, msg)

        if not self.valid_block_transactions(block):
            msg = f"区块内的交易数据验证失败"
            logger.error(msg)
            return ExecuteResult(False, ExecuteResultErrorTypes.BLK_INVALID_TX, msg)

        if self.last_block and (not self.last_block.hash == block.prev_hash):
            msg = f"区块链完整性(prev_hash)数据验证失败"
            logger.error(msg)
            return ExecuteResult(False, ExecuteResultErrorTypes.BLK_INVALID_PREV_HASH, msg)

        return ExecuteResult(True, None, None)

    @bcl.func_lock
    def add_block(self, block: Block | None) -> ExecuteResult:
        """

        :return: bool
        """
        current_txpool = self.current_node.txpool

        # block type check
        if block is None:
            msg = "block为None"
            logger.error(msg)
            return ExecuteResult(False, ExecuteResultErrorTypes.BLK_INVALID_DATA, msg)

        # block validation check
        valid_result: ExecuteResult = self.valid_new_block(block)
        if not valid_result.success:
            return valid_result

        # add block & mark tx verified
        # TODO: 这里应该做一下延迟处理，添加了一个块之后，将第n个之前的块内的所有交易标记为“已确认”
        self.__chain.append(block)
        current_txpool.mark_tx(block)
        msg = f"区块{block.hash}已上链"
        logger.info(msg)

        # 广播区块
        if not block.is_from_peer:
            self.tq.put(self.peer_client.broadcast_block, block)
            logger.info(f"区块{block.hash}广播任务已进入任务队列")

        return ExecuteResult(True, None, msg)

    def serialize(self) -> list[dict]:
        return [b.serialize() for b in self.__chain]

    def serialize_summary(self) -> dict:
        return self.summary.serialize()


class BlockChainSummary:
    __slots__ = ['blocks', 'total_length', 'total_difficulty']

    # 序列化、反序列化时的字段
    serialized_fields = ('blocks', 'total_length', 'total_difficulty')

    def __init__(self, bc: BlockChain):
        self.blocks = [b.summary for b in bc]
        self.total_length = len(bc)
        self.total_difficulty = reduce(lambda x, y: x+y, [bs.difficulty for bs in self.blocks])

    def serialize(self):
        return {
            "blocks": [bs.serialize() for bs in self.blocks],
            "total_length": self.total_length,
            "total_difficulty": self.total_difficulty
        }

    @classmethod
    def deserialize(cls, data: dict | None) -> "BlockChainSummary | None":
        """
        从dict加载数据

        TODO: 反序列化的时候应当进行空值判断，有空值的话就得抛异常
        TODO: 做一个父类出来吧，Serializable的对象，实现serialize、deserialize的方法
        TODO: 然后具备serialized_fields的property方法，返回一个序列化定义
        TODO: {'name': 'xxx', 'type': 'xxx', can_null: True/False}
        TODO: 当type是另一个Serializable对象时，自动调用对应的serialize、deserialize方法，deserialize判断其值必须为dict
        """
        if data is None:
            return None

        bcs = object.__new__(cls)

        for f in cls.serialized_fields:
            fd = data.get(f, None)

            if fd is None:
                continue

            if f == 'blocks':  # 嵌套数据结构特殊处理，调用对应类的反序列化方法
                object.__setattr__(bcs, f, [BlockSummary.deserialize(d) for d in fd])
                continue

            object.__setattr__(bcs, f, fd)

        return bcs

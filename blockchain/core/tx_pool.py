# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node, TaskQueue
    from ..types.core_types import Block
    from ..types.network_types import PeerClient

# std import
import json
from time import time

# local import
from .transaction import Transaction
from ..tools.threading_lock import Lock


txl = Lock()


class TransactionPool:
    def __init__(self, current_node: Node):
        self.current_node = current_node
        self.tq: TaskQueue = self.current_node.task_queue
        self.peer_client: PeerClient = self.current_node.peer_client

        # core
        self.__transactions: list[Transaction] = []

    def __len__(self):
        return len(self.__transactions)

    @txl.func_lock
    def add_transaction(self, transaction: Transaction) -> bool:
        # 支付方为None的情况只有空投奖励,这里只接受其他节点同步过来的数据
        if (transaction.saddr is None) and (not transaction.is_from_peer):
                return False

        # 余额check(系统奖励不进行check)
        if transaction.saddr is not None:
            balance = self.current_node.blockchain.compute_balance(transaction.saddr)
            if transaction.amount > balance:
                print(f'{transaction.saddr} 余额不足')
                return False

        # 交易签名check
        if not transaction.verify_sign():
            print(f'签名校验失败')
            return False

        self.__transactions.append(transaction)
        if not transaction.is_from_peer:  # 广播交易
            self.tq.put(self.peer_client.broadcast_tx, transaction)
        return True

    @txl.func_lock
    def mark_tx(self, block: Block):
        """
        标记区块数据中的交易已确认
        """
        all_confirmed_tx_hashes: list[str] = [t.hash for t in block.transactions]
        for t in self.__transactions:
            if t.hash in all_confirmed_tx_hashes:
                t.mark_confirmed()

    @txl.func_lock
    def clear(self):
        """
        清除交易池中已确认的交易
        """
        not_confirmed_txs = [t for t in self.__transactions if not t.is_confirmed]
        del self.__transactions
        self.__transactions = not_confirmed_txs

    def get_mining_data(self, miner_addr) -> tuple[Transaction, ...]:
        self.clear()
        if len(self) == 0:
            return tuple()

        current_blockchain = self.current_node.blockchain
        # 生成矿工的奖励交易
        reward_tx = Transaction(
            saddr=None,
            raddr=miner_addr,
            amount=current_blockchain.pow_reward,
            timestamp=int(time())
        )

        return tuple(self.__transactions + [reward_tx])

    @txl.func_lock
    def get_prize(self, raddr: str, amount: int) -> bool:
        """
        空投奖励
        """
        prize_tx = Transaction(
            saddr=None,
            raddr=raddr,
            amount=amount,
            timestamp=int(time()),
        )
        self.__transactions.append(prize_tx)

        # 广播这条奖励
        self.tq.put(self.peer_client.broadcast_tx, prize_tx)
        return True

    def to_json(self) -> str:
        return json.dumps([tx.serialize() for tx in self.__transactions], sort_keys=True)

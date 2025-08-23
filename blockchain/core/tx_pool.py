# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.node_types import Node
    from ..types.core_types import Block

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
        self.__transactions: list[Transaction] = []

    def __len__(self):
        return len(self.__transactions)

    @txl.func_lock
    def add_transaction(self, transaction: Transaction) -> bool:
        balance = self.current_node.blockchain.compute_balance(transaction.saddr)
        if transaction.amount > balance:
            print(f'{transaction.saddr} 余额不足')
            return False

        if transaction.saddr is None:
            return False

        if transaction.verify_sign():
            self.__transactions.append(transaction)
            return True
        else:
            print(f'签名校验失败')

        return False

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
        self.__transactions.append(Transaction(
            saddr=None,
            raddr=raddr,
            amount=amount,
            timestamp=int(time()),
        ))
        return True

    def to_json(self) -> str:
        return json.dumps([tx.serialize() for tx in self.__transactions], sort_keys=True)

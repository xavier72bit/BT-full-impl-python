# std import
from time import time

# local import
from blockchain.core.block import Block
from blockchain.core.execute_result import ExecuteResult
from blockchain.core.transaction import Transaction
from blockchain.tools.http_client_json import JSONClient


json_client = JSONClient()


class ProofOfWorkMining:
    def __init__(self, miner_addr: str, node_addr: str):
        self.miner_addr = miner_addr
        self.node_addr = node_addr
        self.pow_check_str = None
        self.difficulty = None

    def get_difficulty(self):
        pow_difficulty = json_client.get(f"{self.node_addr}/pow_difficulty")
        self.pow_check_str = pow_difficulty['hash_startwith']
        self.difficulty = pow_difficulty['difficulty']

    def check_proof(self, block: Block) -> bool:
        if self.pow_check_str is None or self.difficulty is None:
            self.get_difficulty()
        return block.hash.startswith(self.pow_check_str)

    def mine_block(self) -> Block | None:
        """
        :return:
        """
        last_block: Block = Block.deserialize(json_client.get(f"{self.node_addr}/last_block"))
        mining_data: list[Transaction] = [
            Transaction.deserialize(td) for td in json_client.get(f"{self.node_addr}/mining_data/{self.miner_addr}")
        ]

        if not mining_data:
            return None

        nonce = 0
        # 挖矿循环
        while True:
            block = Block(
                index=last_block.index + 1 if last_block else 1,
                timestamp=int(time()),
                transactions=mining_data,
                nonce=nonce,
                prev_hash=last_block.hash if last_block else None,
                difficulty=self.difficulty
            )

            if self.check_proof(block):
                return block

            nonce += 1

    def start_mining(self) -> ExecuteResult:
        block = self.mine_block()
        if block is None:
            return ExecuteResult(success=False, error_type=None, message="交易池无数据")
        return json_client.post(f"{self.node_addr}/block", data=block.serialize())

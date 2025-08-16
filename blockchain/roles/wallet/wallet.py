# std import
import time

# local import
from blockchain.core.transaction import Transaction
from blockchain.tools.ecdsa_sign_tools import ECDSATool
from blockchain.tools.http_json import JSONClient


json_client = JSONClient()


class Wallet:
    """
    console端钱包应用

    创建交易，处理交易余额等等
    """
    def __init__(self, public_key=None, secret_key=None):
        self.pubkey = public_key
        self.seckey = secret_key

        # TODO: 暂时写死
        self.node_addr = 'http://127.0.0.1:5000'

    def generate_transaction(self, raddr, amount):
        """
        生成交易，同时做签署

        :param raddr:
        :param amount:
        :return:
        """
        # 构建交易数据
        tx = Transaction(
            saddr=self.pubkey,
            raddr=raddr,
            amount=amount,
            timestamp=int(time.time())
        )

        # 对交易签名
        tx.sign(self.seckey)

        return json_client.post(self.node_addr + '/transaction', data=tx.serialize())

    def get_balance(self) -> int:
        """
        获取余额

        :return:
        """
        return json_client.get(f'{self.node_addr}/balance/{self.pubkey}')

    @classmethod
    def get_new_wallet(cls) -> "Wallet":
        keys: dict = ECDSATool.generate_keys()
        return cls(public_key=keys['pub'], secret_key=keys['sec'])

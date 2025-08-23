# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : test_script.py
# @Author : Xavier Wu
# @Date   : 2025/8/3 12:54

"""
测试脚本：
运行3-wallet、1-miner
"""
import random
# std import
from time import sleep

# 3rd import
import requests

# local import
from blockchain.core.transaction import Transaction
from blockchain.roles.wallet.wallet import Wallet
from blockchain.roles.mining.pow import ProofOfWorkMining


"""
区块链网络成员
"""
node_addr = 'http://127.0.0.1:5000'

wallet_a = Wallet.get_new_wallet()
wallet_b = Wallet.get_new_wallet()
wallet_c = Wallet.get_new_wallet()
wallets = [wallet_a, wallet_b, wallet_c]

wallet_miner = Wallet.get_new_wallet()
miner = ProofOfWorkMining(wallet_miner.pubkey)


def generate_genesis_block():
    """
    为3个钱包调用空投奖励，然后让矿工挖出创世区块
    """
    for w in wallets:
        resp = requests.get(f'{node_addr}/prize/{w.pubkey}')
        if resp.ok:
            if resp.json():
                print(f"{w.pubkey}获得空投奖励")

    # 让矿工挖出创世区块
    res = miner.start_mining()
    if res:
        print("成功挖出创世区块")
    else:
        print("未成功挖出创世区块")

def ensure_node_alive():
    while True:
        print("尝试连接到node")
        sleep(1)
        is_alive_req = requests.get('http://127.0.0.1:5000/alive')
        if is_alive_req.ok:
            if is_alive_req.json():
                print("node连接成功")
                break

def post_tx(tx: Transaction):
    req = requests.post(f'{node_addr}/transaction', json=tx.serialize())
    if req.ok:
        if req.json():
            print("创建交易成功")
        print("创建交易失败, node拒绝")
    else:
        print("创建交易失败, 网络问题")

def make_some_tx(amount=50):
    """
    模拟一些交易
    """
    for _ in range(amount):
        sender, receiver = random.sample(wallets, 2)
        amount = random.randint(1, 10)

        res = sender.generate_transaction(receiver.pubkey, amount)
        print(f"模拟交易: {sender.pubkey} -> {receiver.pubkey}, {amount}, result: {res}")


if __name__ == '__main__':
    ensure_node_alive()

    # 创世区块
    generate_genesis_block()

    # 模拟一些交易
    make_some_tx()

    # 让矿工挖出区块
    res = miner.start_mining()
    if res:
        print("成功挖出区块")
    else:
        print("未成功挖出区块")

    # 现在应该没有交易了
    res = miner.start_mining()
    if res:
        print("成功挖出区块")
    else:
        print("未成功挖出区块")

    print(requests.get('http://127.0.0.1:5000/blockchain').json())

    print(requests.get('http://127.0.0.1:5000/blockchain/summary').json())

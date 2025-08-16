# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : http_api_server.py
# @Author : Xavier Wu
# @Date   : 2025/8/13 20:35
# 运行在HTTP协议下的API, 服务器使用Flask

# std import
import functools

# 3rd import
from flask import Flask, request, jsonify

# local import
from ..abstract.api_server import API
from ...core.block import Block
from ...core.transaction import Transaction
from ...network.common.peer import NetworkNodePeer


__all__ = ['HTTPAPI']

http = Flask('node-http-api-server')

router_registry = {}
def http_route(rule, **options):
    def decorator(method):
        """
        标记Node类的方法，将其与Flask.route绑定
        并自动处理将返回值：
            1. 正常请求: 包装为json字符串
            2. TODO: 出现异常，返回异常信息
        """
        router_registry[method.__name__] = (rule, options)
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            res = method(self, *args, **kwargs)
            return jsonify(res)
        return wrapper
    return decorator


class HTTPAPI(API):
    @property
    def protocol(self):
        return 'http://'

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

        self.addr = f'{self.protocol}{self.host}:{self.port}'

    def _register_router(self):
        """
        将当前类的方法，与flask app router绑定
        """
        for method_name, flask_router_args in router_registry.items():
            rule, options = flask_router_args
            http.route(rule, **options)(getattr(self, method_name))

    @http_route('/alive', methods=['GET'])
    def _api_alive(self):
        return True

    @http_route('/join', methods=['POST'])
    def _api_join(self):
        """
        接收的请求体为:
        {
            hash: xxx
            protocol: xxx
            addr: xxx
        }

        注册调用该接口的节点信息，并返回自己的所有邻居（包括自己）
        """
        # 先准备好返回值
        self_peers = [np.serialize() for np in self.peer_registry.values()]

        peer_info: dict = request.get_json()
        peer = NetworkNodePeer.deserialize(peer_info)
        if self.peer_registry.add(peer):
            return self_peers

    @http_route('/blockchain', methods=['GET'])
    def _api_download(self):
        """
        下载json格式的区块链数据
        """
        return self.blockchain.to_json()

    @http_route('/block', methods=['POST'])
    def _api_add_block(self):
        block_data: dict = request.get_json()
        block = Block.deserialize(block_data)
        return self.blockchain.add_block(block)

    @http_route('/mining_data/<string:miner_addr>', methods=['GET'])
    def _api_apply_mining_data(self, miner_addr):
        """
        下载json格式的交易池数据
        """
        current_txpool = self.txpool.get_mining_data(miner_addr)
        return [t.serialize() for t in current_txpool]

    @http_route('/last_block', methods=['GET'])
    def _api_last_block(self):
        lb = self.blockchain.last_block
        return lb.serialize() if lb else None

    @http_route('/pow_check', methods=['GET'])
    def _api_pow_check(self):
        return self.blockchain.pow_check

    @http_route('/transaction', methods=['POST'])
    def _api_add_transaction(self):
        tx_data: dict = request.get_json()
        tx = Transaction.deserialize(tx_data)
        return self.txpool.add_transaction(tx)

    @http_route('/balance/<string:addr>')
    def _api_get_balance(self, addr):
        return self.blockchain.compute_balance(addr)

    @http_route('/prize/<string:addr>')
    def _api_prize(self, addr):
        return self.txpool.get_prize(addr, 100)

    @http_route('/broadcast/tx', methods=['POST'])
    def _api_get_broadcast_tx(self):
        tx_data: dict = request.get_json()
        tx = Transaction.deserialize(tx_data)
        tx.mark_from_peer()
        return self.txpool.add_transaction(tx)

    @http_route('/broadcast/block', methods=['POST'])
    def _api_get_broadcast_block(self):
        block_data: dict = request.get_json()
        block = Block.deserialize(block_data)
        block.mark_from_peer()
        return self.blockchain.add_block(block)

    @http_route('/broadcast/peer', methods=['POST'])
    def _api_get_broadcast_peer(self):
        peer_info: dict = request.get_json()
        peer = NetworkNodePeer.deserialize(peer_info)
        return self.peer_registry.add(peer)

    def get_self_peer_info(self):
        return NetworkNodePeer(protocol='http', addr=self.addr)

    def run(self):
        self._register_router()
        http.run(host=self.host, port=self.port)

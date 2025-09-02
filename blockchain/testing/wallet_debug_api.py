# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : wallet_debug_api.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 12:41
# 远程调试用的API, 可以通过控制台开启

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.role_types import Wallet

# std import
import functools
import threading

# 3rd import
from flask import Flask, jsonify, request

# local import
from .debug_api_result import Result
from ..tools.http_client_json import JSONClient
from ..exceptions import TestingNexusAddrNotSpecifiedError


json_client = JSONClient()


wallet_debug_server = Flask('wallet-debug-api-server')
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


class WalletDebugAPI:
    def __init__(self, wallet: Wallet, host, port):
        self.wallet = wallet
        self.host = host
        self.port = port

    def _register_router(self):
        """
        将当前类的方法，与flask app router绑定
        """
        for method_name, flask_router_args in router_registry.items():
            rule, options = flask_router_args
            wallet_debug_server.route(rule, **options)(getattr(self, method_name))

    @http_route('/generate_tx', methods=['POST'])
    def generate_tx(self):
        d: dict = request.get_json()
        raddr: str | None = d.get('raddr')
        amout: int | None = d.get('amount')

        if not all([raddr, amout]):
            return Result(success=False, message="缺少必要参数: 'raddr', 'amount'", data=None).serialize()

        return Result(
            success=True,
            message="成功调用钱包的`generate_transaction`",
            data=self.wallet.generate_transaction(raddr, amout)
        ).serialize()

    def start_server(self):
        self._register_router()
        wallet_debug_server.run(host=self.host, port=self.port)

    def run(self, testing_nexus_addr):
        if not testing_nexus_addr:
            raise TestingNexusAddrNotSpecifiedError("开启debug api，但未指定testing nexus的地址")

        json_client.post(f"{testing_nexus_addr}/registry/wallet", data={
            'publicKey': self.wallet.pubkey,
            'privateKey': self.wallet.seckey,
            'apiAddress': f"http://{self.host}:{self.port}/"
        })

        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        server_thread.join()

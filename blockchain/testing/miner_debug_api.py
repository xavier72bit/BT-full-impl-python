# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : miner_debug_api.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 12:44

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.role_types import ProofOfWorkMining

# std import
import functools
import threading

# 3rd import
from flask import Flask, jsonify

# local import
from .debug_api_result import Result
from ..exceptions import TestingNexusAddrNotSpecifiedError
from ..tools.http_client_json import JSONClient


json_client = JSONClient()


miner_debug_server = Flask('miner-debug-api-server')
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


class MinerDebugAPI:
    def __init__(self, miner: ProofOfWorkMining, host, port):
        self.miner = miner
        self.host = host
        self.port = port

    def _register_router(self):
        """
        将当前类的方法，与flask app router绑定
        """
        for method_name, flask_router_args in router_registry.items():
            rule, options = flask_router_args
            miner_debug_server.route(rule, **options)(getattr(self, method_name))

    @http_route("/mining", methods=['GET'])
    def mining(self):
        t = threading.Thread(target=self._run_mining)
        t.start()

        return Result(success=True, message="已启动挖矿任务", data=None)

    def _run_mining(self):
        self.miner.start_mining().serialize()

    def run_debug_api_server(self):
        self._register_router()
        miner_debug_server.run(host=self.host, port=self.port)

    def run(self):
        server_thread = threading.Thread(target=self.run_debug_api_server, daemon=True)
        server_thread.start()
        server_thread.join()

    def start(self, testing_nexus_addr):
        if not testing_nexus_addr:
            raise TestingNexusAddrNotSpecifiedError("开启debug api，但未指定testing nexus的地址")

        json_client.post(f"{testing_nexus_addr}/registry/miner", data={
            'publicKey': self.miner.miner_addr,
            'apiAddress': f"http://{self.host}:{self.port}/"
        })

        self.run()

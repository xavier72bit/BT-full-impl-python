# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.network_types import API

# std import
import time
import threading

# 3rd import
from loguru import logger

# local import
from ...core.blockchain import BlockChain
from ...core.block import Block
from ...core.tx_pool import TransactionPool
from ...core.consensus import POWConsensus
from ...network.common.peer import NetworkNodePeerRegistry
from ...network.common.peer_client import PeerClient
from .scheduler import Scheduler
from .task_queue import TaskQueue
from .worker import Worker
from ...tools.http_client_json import JSONClient
from ...exceptions import TestingNexusAddrNotSpecifiedError
from ...core.transaction import Transaction


json_client = JSONClient()
__all__ = ["Node"]


class Node:
    """
    隔离的资源容器
    1. coredata
    2. worker - client
    3. api server
    4. scheduler
    """
    def __init__(self, api: API, with_genesis_block: bool):
        """
        由于各个组件资源之间存在相互依赖的关系，这里的执行顺序不可以随意修改
        """
        # 初始化peer_registry, 及其相关参数
        self.peer_registry: NetworkNodePeerRegistry = NetworkNodePeerRegistry()
        self.join_peer = False
        self.join_peer_protocol = None
        self.join_peer_addr = None

        # 去中心化网络通信工具
        self.scheduler = Scheduler()
        self.task_queue = TaskQueue()
        self.worker = Worker(tq=self.task_queue)

        # 初始化peer_client，并建立绑定关系
        self.peer_client = PeerClient()
        self.peer_client.set_node(self)

        # 初始化Core组件(最后初始化，它们依赖task_queue)
        self.blockchain = BlockChain(current_node=self)
        self.txpool = TransactionPool(current_node=self)
        if with_genesis_block:
            self.generate_genesis_block()

        # 设置API, 并建立绑定关系
        self.api = api
        self.api.set_node(self)

        # 初始化自身peer信息
        self_peer_info = self.api.get_self_peer_info()
        self.peer_registry.add(self_peer_info)
        self.self_peer_hash = self_peer_info.hash

        # 初始化共识组件, 同时进行绑定
        self.consensus = POWConsensus(self)

    def set_join_peer(self, protocol: str, addr: str):
        self.join_peer = True
        self.join_peer_protocol = protocol
        self.join_peer_addr = addr

    def _scheduled_function_do_consensus_check(self):
        """
        轮询所有的邻居节点,获取它们的区块链摘要,并调用共识机制处理共识
        """
        self.peer_client.polling_blockchain_summary()

    def _scheduled_function_do_ask_alive(self):
        """
        集群心跳检测
        """
        #TODO
        logger.info("执行集群心跳检测")

    def start_api_server(self):
        self.api.run()
        logger.info(f"API Server 启动")

    def start_scheduler(self):
        self.scheduler.add_interval_job(self._scheduled_function_do_consensus_check, minutes=1, job_name="do_consensus_check")
        self.scheduler.add_interval_job(self._scheduled_function_do_ask_alive, seconds=30, job_name="do_ask_alive")

        self.scheduler.start()
        logger.info(f"Scheduler 启动")

    def start_worker(self):
        """
        启动工作线程
        """
        worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        worker_thread.start()
        logger.info(f"Worker Thread 启动")

    def registry_to_testing_nexus(self, testing_nexus_addr):
        if not testing_nexus_addr:
            raise TestingNexusAddrNotSpecifiedError("未指定testing_nexus_addr")

        res = json_client.post(f"{testing_nexus_addr}/registry/node", data={
            # TODO: 所有的API，无论是network节点之间的API还是nexus testing API，都应实现一个返回调用地址的方法
            "apiAddress": f"http://{self.api.host}:{self.api.port}"
        })

        logger.info(f"注册结果: {res}")

    def start(self):
        if self.join_peer:
            logger.info(f"节点加入网络, 申请节点为: {self.join_peer_protocol}://{self.join_peer_addr}")
            peer_list = self.peer_client.join(self.join_peer_protocol, self.join_peer_addr)
            # TODO: 网络请求错误重试处理（IN PEER CLIENT）
            for peer in peer_list:
                self.peer_registry.add(peer)

        self.start_scheduler()
        self.start_worker()
        self.start_api_server()

    def generate_genesis_block(self):
        if len(self.blockchain):
            logger.warning("无法生成创世区块，区块链非空")
            return

        # TODO: 最开始的测试阶段, hardcode, 私钥备忘: 082484320cf453585e768e16e87837edeb2ab8aa502a951354b527c57f5b81a4
        genesis_address = "49ea27e563177bd60bd9fe529f0787e3323daea48a8d44f7e5094dbc6049fd039855ad607f43a5ae31f63fb098ce5b137b9509c6ab6775d8d11cd1f849ad24d4"
        genesis_transaction = Transaction(saddr=None, raddr=genesis_address, amount=10000, timestamp=int(time.time()))


        # 执行pow的挖矿循环
        nonce = 0
        while True:
            genesis_block = Block(
                index = 1,
                timestamp=int(time.time()),
                transactions=[genesis_transaction],
                nonce=nonce,
                prev_hash=None,
                difficulty=self.blockchain.pow_difficulty
            )
            nonce += 1

            if genesis_block.hash.startswith(self.blockchain.pow_check):
                break

        logger.info(f"创世区块已创建 {genesis_block.serialize()}")
        genesis_block.mark_genesis()

        self.blockchain.add_block(genesis_block)

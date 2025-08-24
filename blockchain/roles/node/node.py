# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.network_types import API

# std import
import threading

# 3rd import
from loguru import logger

# local import
from ...core.blockchain import BlockChain
from ...core.tx_pool import TransactionPool
from ...network.common.peer import NetworkNodePeerRegistry
from ...network.common.peer_client import PeerClient
from .scheduler import Scheduler
from .task_queue import TaskQueue
from .worker import Worker


class Node:
    """
    隔离的资源容器
    1. coredata
    2. worker - client
    3. api server
    4. scheduler
    """
    def __init__(self, api: API):
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

        # 设置API, 并建立绑定关系
        self.api = api
        self.api.set_node(self)

        # 初始化自身peer信息
        self_peer_info = self.api.get_self_peer_info()
        self.peer_registry.add(self_peer_info)
        self.self_peer_hash = self_peer_info.hash

    def set_join_peer(self, protocol: str, addr: str):
        self.join_peer = True
        self.join_peer_protocol = protocol
        self.join_peer_addr = addr

    def _scheduled_function_sync_blockchain(self):
        """
        轮询所有的邻居节点,获取它们的区块链摘要,并调用共识机制处理共识
        """
        pass

    def _scheduled_function_ask_alive(self):
        """
        集群心跳检测
        """
        pass

    def start_api_server(self):
        self.api.run()
        logger.info(f"API Server 启动")

    def start_scheduler(self):
        logger.info(f"Scheduler 启动")

    def start_worker(self):
        """
        启动工作线程
        """
        worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        worker_thread.start()
        logger.info(f"Worker Thread 启动")

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

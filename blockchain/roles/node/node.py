# type hint
# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.network_types import API

# local import
from ...core.blockchain import BlockChain
from ...core.tx_pool import TransactionPool
from ...network.common.peer import NetworkNodePeerRegistry
from ...network.common.peer_client import PeerClient


class Node:
    def __init__(self, api: API):
        # 初始化Core组件
        self.blockchain = BlockChain(current_node=self)
        self.txpool = TransactionPool(current_node=self)

        # 初始化peer_registry
        self.peer_registry: NetworkNodePeerRegistry = NetworkNodePeerRegistry()

        # 设置API, 并建立绑定关系
        self.api = api
        self.api.set_node(self)

        # 初始化peer_client，并建立绑定关系
        self.peer_client = PeerClient()
        self.peer_client.set_node(self)

        # 初始化自身peer信息
        self.peer_registry.add(self.api.get_self_peer_info())

        # 其他运行时参数
        self.join_peer = False
        self.join_peer_protocol = None
        self.join_peer_addr = None

    def set_join_peer(self, protocol: str, addr: str):
        self.join_peer = True
        self.join_peer_protocol = protocol
        self.join_peer_addr = addr

    def start(self):
        if self.join_peer:
            print("节点加入网络")
            peer_list = self.peer_client.join(self.join_peer_protocol, self.join_peer_addr)
            for peer in peer_list:
                self.peer_registry.add(peer)

        print(f"节点启动, peer信息: {[p.serialize() for p in self.peer_registry]}")
        self.api.run()

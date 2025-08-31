# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.node_types import Node, TaskQueue
    from ...types.network_types import PeerClientAdapter, NetworkNodePeerRegistry
    from ...types.core_types import Transaction, Block, POWConsensus

# 3rd import
from loguru import logger

# local import
from .peer import NetworkNodePeer
from ..http.http_peer_client_adapter import HTTPPeerClientAdapter
from ...exceptions import PeerClientAdapterProtocolError
from ...core.blockchain import BlockChainSummary


class PeerClient:
    def __init__(self):
        self.node = None
        self.current_peers = None

    def set_node(self, node: Node):
        self.node = node
        self.current_peers: NetworkNodePeerRegistry = self.node.peer_registry

    def get_adapter(self, protocol: str) -> PeerClientAdapter:
        res = {
            'http': HTTPPeerClientAdapter()
        }.get(protocol, None)

        if res is None:
            raise PeerClientAdapterProtocolError(f"Not Found Adapter, protocol: {protocol}")
        else:
            return res

    def join(self, protocol, addr) -> list[NetworkNodePeer]:
        """
        向网络成员节点发送加入网络请求
        """
        adapter = self.get_adapter(protocol)
        self_peer_info = self.node.api.get_self_peer_info()
        join_peer_info = NetworkNodePeer(protocol=protocol, addr=addr)

        return adapter.join_network(join_peer_info, self_peer_info)

    def _send_tx(self, peer: NetworkNodePeer, tx: Transaction):
        adapter = self.get_adapter(peer.protocol)
        return adapter.send_tx(peer, tx)

    def _send_block(self, peer: NetworkNodePeer, block: Block):
        adapter = self.get_adapter(peer.protocol)
        return adapter.send_block(peer, block)

    def _send_peer(self, peer: NetworkNodePeer, send_peer: NetworkNodePeer):
        adapter = self.get_adapter(peer.protocol)
        return adapter.send_peer(peer, send_peer)

    def _get_blockchain_summary(self, peer: NetworkNodePeer):
        adapter = self.get_adapter(peer.protocol)
        return adapter.get_blockchain_summary(peer)

    def broadcast_block(self, block: Block):
        for peer in self.current_peers:
            if peer.hash == self.node.self_peer_hash:
                continue
            self._send_block(peer, block)

    def broadcast_tx(self, tx: Transaction):
        for peer in self.current_peers:
            if peer.hash == self.node.self_peer_hash:
                continue
            self._send_tx(peer, tx)

    def broadcast_peer(self, send_peer: NetworkNodePeer):
        for peer in self.current_peers:
            if peer.hash == self.node.self_peer_hash:
                continue
            self._send_peer(peer, send_peer)

    def request_block_chain_data(self, peer: NetworkNodePeer):
        """
        获取指定邻居节点的区块链数据
        """
        return self.get_adapter(peer.protocol).get_blockchain_data(peer)

    def polling_blockchain_summary(self):
        """
        轮询邻居节点的区块链摘要信息, 并交给共识组件进行处理
        """
        tq: TaskQueue = self.node.task_queue
        cons: POWConsensus = self.node.consensus
        for peer in self.current_peers:
            if peer.hash == self.node.self_peer_hash:
                continue
            bc_summary_data = self._get_blockchain_summary(peer)

            tq.put(cons.check_summary, BlockChainSummary.deserialize(bc_summary_data), peer)
            logger.info(f"新增共识检查Task, 节点对象: {peer.hash}")

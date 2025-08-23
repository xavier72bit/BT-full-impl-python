# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.node_types import Node
    from ...types.network_types import PeerClientAdapter, NetworkNodePeerRegistry
    from ...types.core_types import Transaction, Block

from .peer import NetworkNodePeer
from ..http.http_peer_client_adapter import HTTPPeerClientAdapter
from ...exceptions import PeerClientAdapterProtocolError


class PeerClient:
    def __init__(self):
        self.node = None
        self.current_peers = None
        self.self_peer_hash = None

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

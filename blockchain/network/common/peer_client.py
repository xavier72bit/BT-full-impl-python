# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.node_types import Node
    from ...types.network_types import PeerClientAdapter

from .peer import NetworkNodePeer
from ..http.http_peer_client_adapter import HTTPPeerClientAdapter
from ...exceptions import PeerClientAdapterProtocolError


class PeerClient:
    def __init__(self):
        self.node = None

    def set_node(self, node: Node):
        self.node = node

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

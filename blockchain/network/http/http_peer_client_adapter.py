# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : http_peer_client_adapter.py
# @Author : Xavier Wu
# @Date   : 2025/8/13 20:35

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.core_types import Transaction, Block

# 3rd import
import requests

# local import
from ..abstract.peer_client_adapter import PeerClientAdapter
from ...exceptions import PeerClientAdapterProtocolError
from ..common.peer import NetworkNodePeer


class HTTPPeerClientAdapter(PeerClientAdapter):
    @property
    def protocol(self) -> str:
        return 'http'

    def check_peer_protocol(self, peer: NetworkNodePeer):
        if peer.protocol != self.protocol:
            raise PeerClientAdapterProtocolError(f'peer: {peer.protocol}, adapter: {self.protocol}')

    def send_block(self, peer: NetworkNodePeer, block: Block):
        self.check_peer_protocol(peer)
        raise NotImplementedError

    def send_tx(self, peer: NetworkNodePeer, tx: Transaction):
        self.check_peer_protocol(peer)
        raise NotImplementedError

    def send_peer(self, peer: NetworkNodePeer, send_peer_info: NetworkNodePeer):
        self.check_peer_protocol(peer)
        raise NotImplementedError

    def join_network(self, peer: NetworkNodePeer, self_peer_info: NetworkNodePeer) -> list[NetworkNodePeer] | None:
        api_path = '/join'
        self.check_peer_protocol(peer)

        response = requests.post(url=f"{peer.addr}{api_path}", json=self_peer_info.serialize())
        if response.ok:
            if peer_data := response.json():
                return [NetworkNodePeer.deserialize(pd) for pd in peer_data]

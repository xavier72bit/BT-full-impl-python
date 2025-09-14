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

# local import
from ..abstract.peer_client_adapter import PeerClientAdapter
from ...exceptions import PeerClientAdapterProtocolError
from ..common.peer import NetworkNodePeer
from ...tools.http_client_json import JSONClient


json_client = JSONClient()


class HTTPPeerClientAdapter(PeerClientAdapter):
    @property
    def protocol(self) -> str:
        return 'http'

    def check_peer_protocol(self, peer: NetworkNodePeer):
        if peer.protocol != self.protocol:
            raise PeerClientAdapterProtocolError(f'peer: {peer.protocol}, adapter: {self.protocol}')

    def send_block(self, peer: NetworkNodePeer, block: Block):
        self.check_peer_protocol(peer)
        api_path = '/broadcast/block'
        return json_client.post(url=f"{peer.addr}{api_path}", data=block.serialize())

    def send_tx(self, peer: NetworkNodePeer, tx: Transaction):
        self.check_peer_protocol(peer)
        api_path = '/broadcast/tx'
        return json_client.post(url=f"{peer.addr}{api_path}", data=tx.serialize())

    def send_peer(self, peer: NetworkNodePeer, send_peer_info: NetworkNodePeer):
        self.check_peer_protocol(peer)
        api_path = '/broadcast/peer'

        return json_client.post(url=f"{peer.addr}{api_path}", data=send_peer_info.serialize())

    def get_blockchain_summary(self, peer: NetworkNodePeer):
        self.check_peer_protocol(peer)
        api_path = '/blockchain/summary'

        return json_client.get(url=f"{peer.addr}{api_path}")

    def get_blockchain_data(self, peer: NetworkNodePeer) -> dict:
        self.check_peer_protocol(peer)
        api_path = '/blockchain'

        return json_client.get(url=f"{peer.addr}{api_path}")

    def join_network(self, peer: NetworkNodePeer, self_peer_info: NetworkNodePeer) -> list[NetworkNodePeer] | None:
        self.check_peer_protocol(peer)
        api_path = '/join'

        resp = json_client.post(url=f"{peer.addr}{api_path}", data=self_peer_info.serialize())
        if resp:
            return [NetworkNodePeer.deserialize(pd) for pd in resp]

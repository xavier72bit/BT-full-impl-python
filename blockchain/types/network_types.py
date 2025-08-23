# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : network_types.py
# @Author : Xavier Wu
# @Date   : 2025/8/13 20:44
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..network.abstract.api_server import API
    from ..network.abstract.peer_client_adapter import PeerClientAdapter
    from ..network.common.peer import NetworkNodePeer, NetworkNodePeerRegistry
    from ..network.common.peer_client import PeerClient

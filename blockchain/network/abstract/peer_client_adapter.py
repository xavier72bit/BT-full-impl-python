# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.core_types import Transaction, Block
    from ...types.network_types import NetworkNodePeer

# std import
from abc import abstractmethod, ABC


__all__ = ['PeerClientAdapter']


class PeerClientAdapter(ABC):
    @abstractmethod
    def protocol(self) -> str:
        """
        标记当前adapter适配的网络协议
        """
        pass

    @abstractmethod
    def send_tx(self, peer: NetworkNodePeer, tx: Transaction):
        """
        将交易信息发送给网络节点
        """
        pass

    @abstractmethod
    def send_block(self, peer: NetworkNodePeer, block: Block):
        """
        将区块数据发送给网络节点
        """
        pass

    @abstractmethod
    def send_peer(self, peer: NetworkNodePeer, send_peer: NetworkNodePeer):
        """
        将联系自己邻居分享给自己的其他邻居
        """
        pass

    @abstractmethod
    def get_blockchain_summary(self, peer: NetworkNodePeer):
        """
        获取邻居的区块链摘要数据
        """
        pass

    @abstractmethod
    def get_blockchain_data(self, peer: NetworkNodePeer):
        """
        获取邻居的区块链数据
        """
        pass

    @abstractmethod
    def join_network(self, peer: NetworkNodePeer, self_peer_info: NetworkNodePeer):
        """
        向指定的网络节点发送加入请求
        """
        pass

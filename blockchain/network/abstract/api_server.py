# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...types.node_types import Node
    from ...types.network_types import NetworkNodePeer

# std import
from abc import abstractmethod, ABC


__all__ = ['API']


class API(ABC):
    def __init__(self):
        self.node = None
        self.blockchain = None
        self.txpool = None
        self.peer_registry = None

    def set_node(self, node: Node):
        self.node = node
        self.blockchain = self.node.blockchain
        self.txpool = self.node.txpool
        self.peer_registry = self.node.peer_registry

    ################################################
    # Node API
    ################################################

    @abstractmethod
    def _api_alive(self):
        """
        心跳检测
        """
        pass

    @abstractmethod
    def _api_join(self):
        """
        请求节点加入网络
        """
        pass

    @abstractmethod
    def _api_get_broadcast_tx(self):
        """
        从其他节点的广播获取交易信息
        peer client --> api server
        """
        pass

    @abstractmethod
    def _api_get_broadcast_block(self):
        """
        从其他节点的广播获取区块信息
        peer client --> api server
        """
        pass

    @abstractmethod
    def _api_get_broadcast_peer(self):
        """
        从其他节点获取广播成员加入信息
        """
        pass

    ################################################
    # BlockChain API
    ################################################

    @abstractmethod
    def _api_download(self):
        """
        下载区块链数据
        """
        pass

    @abstractmethod
    def _api_add_block(self):
        """
        添加区块
        """

    @abstractmethod
    def _api_last_block(self):
        """
        获取最后一个区块的数据
        """
        pass

    ################################################
    # Mining API
    ################################################

    @abstractmethod
    def _api_apply_mining_data(self):
        """
        申请挖矿的区块数据
        """
        pass

    @abstractmethod
    def _api_pow_difficulty(self):
        """
        检查Proof of Work
        """
        pass

    ################################################
    # user & transaction API
    ################################################

    @abstractmethod
    def _api_add_transaction(self):
        """
        新增交易数据
        """
        pass

    @abstractmethod
    def _api_get_balance(self, addr):
        """
        获取指定地址的余额
        """
        pass

    @abstractmethod
    def _api_prize(self, addr):
        """
        给指定地址空投奖励
        """
        pass


    ################################################
    # object function
    ################################################

    @abstractmethod
    def get_self_peer_info(self) -> NetworkNodePeer:
        """
        获取其他node调用自己的peer info
        """
        pass

    @abstractmethod
    def run(self):
        """
        启动API服务
        """
        pass

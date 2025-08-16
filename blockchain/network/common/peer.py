# local import
from blockchain.tools.hash_tools import compute_hash
from ...exceptions import PeerClientProtocolError
from ...exceptions import DeserializeHashValueCheckError

all_peer_protocol = ('http',)


class NetworkNodePeer:
    """
    标记区块链中的其他的节点信息
    """
    __slots__ = ['protocol', 'addr', 'hash']
    frozen_fields = ('protocol', 'addr', 'hash')

    def __init__(self, protocol: str, addr: str):
        """
        拿http node举例:
            * protocol: http
            * addr: http://127.0.0.1:5000/
        """
        if protocol not in all_peer_protocol:
            raise PeerClientProtocolError(f"Not found protocol: {protocol} all supported: {all_peer_protocol}")

        object.__setattr__(self, 'protocol', protocol)
        object.__setattr__(self, 'addr', addr)

        object.__setattr__(self,'hash', self.compute_hash())

    def peer_core_data(self):
        return {
            'protocol': self.protocol,
            'addr': self.addr
        }

    def compute_hash(self):
        return compute_hash(self.peer_core_data())

    @classmethod
    def deserialize(cls, data: dict | None) -> "NetworkNodePeer | None":
        if data is None:
            return None

        np = object.__new__(cls)
        for f in cls.__slots__:
            if f == 'hash':  # 跳过hash字段的赋值
                continue
            object.__setattr__(np, f, data.get(f, None))

        # hash一致性检查
        computed_hash = np.compute_hash()
        data_hash = data.get('hash', None)
        if computed_hash == data_hash:
            object.__setattr__(np, 'hash', computed_hash)
        else:
            raise DeserializeHashValueCheckError(f"Peer Data compute hash: {computed_hash}, data hash: {data_hash}")

        return np

    def serialize(self) -> dict:
        d = {}
        for f in self.__slots__:
            d[f] = getattr(self, f)
        return d


class NetworkNodePeerRegistry:
    """
    维护当前区块链网络的节点信息
    """
    def __init__(self):
        self.__peers: dict[str, NetworkNodePeer] = {}

    def __contains__(self, item):
        return item in self.__peers

    def __len__(self):
        return len(self.__peers)

    def __getitem__(self, item):
        return self.__peers[item]

    def __iter__(self):
        return self.__peers.values().__iter__()

    def keys(self):
        return self.__peers.keys()

    def values(self):
        return self.__peers.values()

    def items(self):
        return self.__peers.items()

    def get(self, peer_hash) -> NetworkNodePeer | None:
        return self.__peers.get(peer_hash, None)

    def add(self, node_peer: NetworkNodePeer) -> bool:
        if node_peer.hash in self.keys():
            return False
        else:
            self.__peers[node_peer.hash] = node_peer
            return True

    def delete(self, peer_hash) -> bool:
        if peer_hash in self.keys():
            return False
        else:
            del self.__peers[peer_hash]
            return True

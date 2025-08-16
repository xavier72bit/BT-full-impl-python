# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : exceptions.py
# @Author : Xavier Wu
# @Date   : 2025/8/16 14:03

# Hash Check Error
class DeserializeHashValueCheckError(Exception):
    """
    反序列化时的hash检查未通过
    """
    pass

# network
class PeerClientProtocolError(Exception):
    """
    邻居Node的Protocol不支持
    """
    pass


class PeerClientAdapterProtocolError(Exception):
    """
    PeerClient所运行的网络协议与Adapter不匹配
    """
    pass

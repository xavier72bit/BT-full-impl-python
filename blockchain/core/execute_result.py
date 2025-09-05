# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : execute_result.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 13:20

from dataclasses import dataclass, asdict


class ExecuteResultErrorTypes:

    """
    交易验证类
    """
    TX_REPEAT = 10  # 交易重复
    TX_SADDR_NONE = 11  # 伪造系统交易
    TX_INSUFFICIENT_BALANCE = 12  # 余额不足
    TX_INVALID_SIGNATURE = 13   # 签名验证失败

    """
    区块验证类
    """
    BLK_INVALID_POW = 20 # proof of work 验证失败
    BLK_INVALID_TX = 21 # 区块的交易数据验证失败
    BLK_INVALID_HASH = 22 # 区块的hash验证失败
    BLK_INVALID_PREV_HASH = 23 # 区块的前hash数据验证失败
    BLK_INVALID_DATA = 24 # 区块链的数据结构无效


@dataclass
class ExecuteResult:
    """
    当函数返回值需要描述“操作成功”/“操作失败”的语义时，返回此包装类
    """
    success: bool
    error_type: int | None
    message: str | None

    def serialize(self):
        return asdict(self)

    @classmethod
    def deserialize(cls, data: dict) -> "ExecuteResult":
        return cls(
            success=data.get("success", False),
            error_type=data.get("error_type", None),
            message=data.get("message", None)
        )

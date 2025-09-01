# -*- coding: UTF-8 -*-
# @Project: BT-full-impl-python
# @File   : wallet_debug_api.py
# @Author : Xavier Wu
# @Date   : 2025/9/1 12:41
# 远程调试用的API, 可以通过控制台开启

# types hint
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..types.role_types import Wallet


class WalletDebugAPI:

    def __init__(self, wallet: Wallet):
        self.wallet = wallet

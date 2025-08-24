from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List
    from ..core.block import Block, BlockSummary
    from ..core.blockchain import BlockChain, BlockChainSummary
    from ..core.transaction import Transaction
    from ..core.tx_pool import TransactionPool

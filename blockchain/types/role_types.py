from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..roles.node.node import Node
    from ..roles.node.task_queue import TaskQueue
    from ..roles.node.scheduler import Scheduler
    from ..roles.node.worker import Worker

    from ..roles.wallet.wallet import Wallet

    from ..roles.mining.pow import ProofOfWorkMining

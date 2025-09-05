# std import
import sys
import argparse

# local import
from blockchain.roles.node.node import Node
from blockchain.roles.wallet.wallet import Wallet
from blockchain.roles.mining.pow import ProofOfWorkMining

# 角色支持的类型定义 Const
SUPPORTED_ROLE_TYPES = {
    "wallet": [],
    "miner": [],  # TODO: 这里可以选择不同的工作量证明机制, 比如PoW, PoS
    "node": ["http"],
}

################################################
# bin args
################################################

parser = argparse.ArgumentParser(description="Run the blockchain component.")
parser.add_argument(
    "-r", "--role",
    type=str,
    required=True,
    choices=SUPPORTED_ROLE_TYPES.keys(),
    help=f"Choose a role: {', '.join(SUPPORTED_ROLE_TYPES.keys())}"
)

parser.add_argument(
    "-t", "--type",
    type=str,
    default=None,
    help="Specify role type (depends on role)"
)

parser.add_argument(
    "-H", "--host",
    type=str,
    default="127.0.0.1",
    help="Host address (default: 127.0.0.1)"
)

parser.add_argument(
    "-p", "--port",
    type=int,
    default=5000,
    help="Port number (default: 5000)"
)

parser.add_argument(
    "--join-peer-protocol",
    type=str,
    default=None,
    choices=SUPPORTED_ROLE_TYPES['node'],
    help="Protocol used to connect to peer node"
)

parser.add_argument(
    "--join-peer-addr",
    type=str,
    default=None,
    help="Address of the peer node to connect to (need to add protocol, e.g. http://127.0.0.1)"
)

parser.add_argument(
    "--with-genesis-block",
    action="store_true",
    help="When the node starts, whether to automatically generate the genesis block"
)

parser.add_argument(
    "--using-testing-nexus",
    action="store_true",
    help="Choose whether to enable the Debug API Server (valid only for wallet and miner) or registry to testing nexus"
)

parser.add_argument(
    "--testing-nexus-addr",
    type=str,
    default=None,
    help="Specify the API address of the testing nexus"
)

parser.add_argument(
    "--public-key",
    type=str,
    default=None,
    help="Public key address (used by miners/wallets)"
)

parser.add_argument(
    "--private-key",
    type=str,
    default=None,
    help="Private key (used by wallets)"
)

parser.add_argument(
    "--generate-wallet",
    action="store_true",
    help="generates an electronic wallet (Only supports -r wallet)"
)

parser.add_argument(
    "--connect-node-addr",
    type=str,
    default=None,
    help="wallet, miner connected to the node address"
)

################################################
# main functions
################################################

def run_wallet(
        # wallet info
        public_key, secret_key, connect_node_addr,
        # debug api
        host, port,
        # testing nexus connection
        using_testing_nexus: bool, testing_nexus_addr
    ):
    # TODO: Wallet GUI界面
    wallet = Wallet(public_key, secret_key)

    if connect_node_addr:
        wallet.login(connect_node_addr)

    if using_testing_nexus:  # 最后执行
        from blockchain.testing.wallet_debug_api import WalletDebugAPI
        server = WalletDebugAPI(wallet, host, port)
        server.start(testing_nexus_addr)

def generate_wallet():
    new_wallet = Wallet.get_new_wallet()
    print(f"Public Key(wallet address): <{new_wallet.pubkey}>")
    print(f"Secret Key(wallet password, Never disclose!!): <{new_wallet.seckey}>")

def run_miner(public_key, connect_node_addr, host, port, using_testing_nexus: bool, testing_nexus_addr):
    #TODO: Miner GUI界面
    miner = ProofOfWorkMining(miner_addr=public_key, node_addr=connect_node_addr)

    if using_testing_nexus:
        from blockchain.testing.miner_debug_api import MinerDebugAPI
        MinerDebugAPI(miner, host, port).start(testing_nexus_addr)

def run_node_http(
        # node info
        host, port, join_peer_protocol=None, join_peer_addr=None,
        # testing nexus connection
        using_testing_nexus: bool = False, testing_nexus_addr = None,
        # blockchain info
        with_genesis_block: bool = False
    ):
    from blockchain.network.http.http_api_server import HTTPAPI
    http_api = HTTPAPI(host, port)
    node = Node(api=http_api, with_genesis_block=with_genesis_block)

    if join_peer_addr and join_peer_protocol:
        node.set_join_peer(join_peer_protocol, join_peer_addr)

    if using_testing_nexus:
        node.registry_to_testing_nexus(testing_nexus_addr)

    node.start()

################################################
# main entrypoint
################################################

def main():
    args = parser.parse_args()

    # 检查类型是否受支持
    valid_types = SUPPORTED_ROLE_TYPES[args.role]
    if valid_types:
        if args.type not in valid_types:
            print(
                f"Invalid type '{args.type}' for role '{args.role}'. "
                f"Supported types: {', '.join(valid_types)}",
                file=sys.stderr
            )
            sys.exit(1)
    else:
        if args.type:
            print(f"Role '{args.role}' does not support type parameter.", file=sys.stderr)
            sys.exit(1)

    # 根据角色分发
    if args.role == "wallet":
        if args.generate_wallet:
            generate_wallet()
            return

        run_wallet(
            args.public_key, args.private_key, args.connect_node_addr,
            args.host, args.port,
            args.using_testing_nexus, args.testing_nexus_addr
        )

    elif args.role == "miner":
        run_miner(
            args.public_key, args.connect_node_addr,
            args.host, args.port,
            args.using_testing_nexus, args.testing_nexus_addr
        )

    elif args.role == "node":
        if args.type == "http":
            with_gb = True if args.with_genesis_block else False
            run_node_http(
                args.host, args.port, args.join_peer_protocol, args.join_peer_addr,
                args.using_testing_nexus, args.testing_nexus_addr,
                with_gb
            )
        else:
            print(f"Node type '{args.type}' is not supported.", file=sys.stderr)
            sys.exit(1)

    else:
        print("Invalid role specified.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

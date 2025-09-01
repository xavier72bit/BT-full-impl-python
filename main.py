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
    "--debug-api-server",
    action="store_true",
    help="Choose whether to enable the Debug API Server (valid only for wallet and miner)"
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

################################################
# main functions
################################################

def run_wallet(public_key, secret_key, enable_debug_api_server: bool, host, port):
    # TODO: Wallet GUI界面
    wallet = Wallet(public_key, secret_key)
    if enable_debug_api_server:
        from blockchain.testing.wallet_debug_api import WalletDebugAPI
        server = WalletDebugAPI(wallet, host, port)
        server.run()

def run_miner(_type):
    print(f"Running miner (type={_type})")
    # TODO: 实现矿工逻辑

def run_node_http(host, port, join_peer_protocol=None, join_peer_addr=None):
    from blockchain.network.http.http_api_server import HTTPAPI
    http_api = HTTPAPI(host, port)
    node = Node(api=http_api)

    if join_peer_addr and join_peer_protocol:
        node.set_join_peer(join_peer_protocol, join_peer_addr)

    node.start()

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
        run_wallet(args.public_key, args.private_key, args.debug_api_server, args.host, args.port)

    elif args.role == "miner":
        run_miner(args.type)

    elif args.role == "node":
        if args.type == "http":
            run_node_http(args.host, args.port, args.join_peer_protocol, args.join_peer_addr)
        else:
            print(f"Node type '{args.type}' is not supported.", file=sys.stderr)
            sys.exit(1)

    else:
        print("Invalid role specified.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

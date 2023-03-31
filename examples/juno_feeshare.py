"""Example of juno feeshare."""
import argparse

from pyuno.aerial.client.config import NetworkConfig
from pyuno.aerial.client import LedgerClient


def _parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract_address", help="feeshare contract address", required=False
    )
    parser.add_argument(
        "--withdrawer_address", help="feeshare withdrawer address", required=False
    )
    parser.add_argument(
        "--deployer_address", help="feeshare deployer address", required=False
    )

    return parser.parse_args()


def main():
    """Run main."""
    network_config = NetworkConfig.cosmos_directory_juno_mainnet()

    ledger_client = LedgerClient(network_config)

    args = _parse_commandline()

    contract_address = args.contract_address
    withdrawer_address = args.withdrawer_address
    deployer_address = args.deployer_address

    if contract_address:
        print(
            f"feshares: {ledger_client.query_fee_share_by_contract(contract_address)}"
        )

    if withdrawer_address:
        resp = ledger_client.query_fee_shares_by_withdrawer(withdrawer_address)
        print(f"contract_addresses: {resp}")

    if deployer_address:
        resp = ledger_client.query_fee_shares_by_deployer(deployer_address)
        print(f"contract_addresses: {resp}")
        resp = ledger_client.query_bal

    if not contract_address and not withdrawer_address and not deployer_address:
        print(f"feeshares: {ledger_client.query_all_fee_shares()}")


if __name__ == "__main__":
    main()

from junopy.aerial.client import LedgerClient, NetworkConfig


def main():
    ledger = LedgerClient(NetworkConfig.juno_mainnet())

    _ = ledger.query_all_fee_shares()


if __name__ == "__main__":
    main()

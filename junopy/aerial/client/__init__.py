import json
from dataclasses import dataclass
from typing import Iterable, Dict, Optional

import certifi
import cosmpy.aerial.client
import grpc
from cosmpy.aerial.client import prepare_and_broadcast_basic_transaction
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.tx_helpers import SubmittedTx
from cosmpy.aerial.urls import parse_url, Protocol
from cosmpy.aerial.wallet import Wallet
from cosmpy.common.rest_client import RestClient
from cosmpy.crypto.address import Address

from junopy.aerial.client.config import NetworkConfig
from junopy.aerial.client.feeshare import (
    create_register_feeshare_msg,
    create_update_feeshare_msg,
    create_cancel_feeshare_msg,
)
from junopy.feeshare.rest_client import FeeShareRestClient
from junopy.protos.juno.feeshare.v1.query_pb2 import (
    QueryFeeSharesRequest,
    QueryFeeShareRequest,
    QueryDeployerFeeSharesRequest,
    QueryWithdrawerFeeSharesRequest,
    QueryParamsRequest,
)

from junopy.protos.juno.feeshare.v1.query_pb2_grpc import (
    QueryStub as FeeShareGrpcClient,
)

DEFAULT_QUERY_TIMEOUT_SECS = 15
DEFAULT_QUERY_INTERVAL_SECS = 2
JUNO_SDK_DEC_COIN_PRECISION = 10**6


@dataclass
class FeeShare:
    """FeeShare."""

    contract_address: str
    deployer_address: str
    withdrawer_address: str


class LedgerClient(cosmpy.aerial.client.LedgerClient):
    def __init__(
        self,
        cfg: cosmpy.aerial.client.NetworkConfig = None,
        query_interval_secs: int = DEFAULT_QUERY_INTERVAL_SECS,
        query_timeout_secs: int = DEFAULT_QUERY_TIMEOUT_SECS,
    ):
        if cfg is None:
            cfg = NetworkConfig.juno_mainnet()
        super().__init__(cfg, query_interval_secs, query_timeout_secs)

        parsed_url = parse_url(cfg.url)

        if parsed_url.protocol == Protocol.GRPC:
            if parsed_url.secure:
                with open(certifi.where(), "rb") as f:
                    trusted_certs = f.read()
                credentials = grpc.ssl_channel_credentials(
                    root_certificates=trusted_certs
                )
                grpc_client = grpc.secure_channel(parsed_url.host_and_port, credentials)
            else:
                grpc_client = grpc.insecure_channel(parsed_url.host_and_port)

            self.fee_share = FeeShareGrpcClient(grpc_client)
        else:
            rest_client = RestClient(parsed_url.rest_url)
            self.fee_share = FeeShareRestClient(rest_client)

    def query_all_fee_shares(self) -> Iterable[FeeShare]:
        """Query all feeshares.

        :param address: address to query
        :return: all feeshares
        """
        fee_shares = self.fee_share.FeeShares(QueryFeeSharesRequest())
        return [
            FeeShare(
                contract_address=fee_share.contract_address,
                deployer_address=fee_share.deployer_address,
                withdrawer_address=fee_share.deployer_address,
            )
            for fee_share in fee_shares.feeshare
        ]

    def query_fee_share_by_contract(self, contract_address: str) -> FeeShare:
        """Query the fee share of an address.

        :param address: address to query
        :return: fee share of the address
        """
        req = QueryFeeShareRequest(contract_address=contract_address)
        res = self.fee_share.FeeShare(req)
        return FeeShare(
            contract_address=res.feeshare.contract_address,
            deployer_address=res.feeshare.deployer_address,
            withdrawer_address=res.feeshare.deployer_address,
        )

    def query_fee_shares_by_deployer(self, deployer_address: str) -> Iterable[str]:
        """Query feeshares by deployer.

        :param deployer_address: address to query
        :return: feeshares of the deployer
        """
        req = QueryDeployerFeeSharesRequest(deployer_address=deployer_address)
        res = self.fee_share.DeployerFeeShares(req)
        return [contract_address for contract_address in res.contract_addresses]

    def query_fee_shares_by_withdrawer(self, withdrawer_address: str) -> Iterable[str]:
        """Query feeshares by withdrawer.

        :param withdrawer_address: address to query
        :return: feeshares of the withdrawer
        """
        req = QueryWithdrawerFeeSharesRequest(withdrawer_address=withdrawer_address)
        res = self.fee_share.WithdrawerFeeShares(req)
        return [contract_address for contract_address in res.contract_addresses]

    def query_fee_shares_params(self) -> Dict:
        """Query fee shares params.

        :return: fee shares params
        """
        resp = self.fee_share.Params(QueryParamsRequest())

        return json.loads(resp.param.value)

    def register_fee_share(
        self,
        contract_address: Address,
        withdrawer_address: Address,
        sender: Wallet,
        memo: Optional[str] = None,
        gas_limit: Optional[int] = None,
    ) -> SubmittedTx:
        """Register fee share.

        :param contract_address: contract address
        :param withdrawer_address: withdrawer address
        :param sender: sender
        :param memo: memo, defaults to None
        :param gas_limit: gas limit, defaults to None
        :return: submitted tx
        """
        # build up the register fee share message
        tx = Transaction()
        tx.add_message(
            create_register_feeshare_msg(
                sender.address(), contract_address, withdrawer_address
            )
        )
        return prepare_and_broadcast_basic_transaction(
            self, tx, sender, gas_limit=gas_limit, memo=memo
        )

    def update_fee_share(
        self,
        contract_address: Address,
        withdrawer_address: Address,
        sender: Wallet,
        memo: Optional[str] = None,
        gas_limit: Optional[int] = None,
    ) -> SubmittedTx:
        """Update fee share.

        :param contract_address: contract address
        :param withdrawer_address: withdrawer address
        :param sender: sender
        :param memo: memo, defaults to None
        :param gas_limit: gas limit, defaults to None
        :return: submitted tx
        """
        # build up the update fee share message
        tx = Transaction()
        tx.add_message(
            create_update_feeshare_msg(
                sender.address(), contract_address, withdrawer_address
            )
        )
        return prepare_and_broadcast_basic_transaction(
            self, tx, sender, gas_limit=gas_limit, memo=memo
        )

    def cancel_fee_share(
        self,
        contract_address: Address,
        sender: Wallet,
        memo: Optional[str] = None,
        gas_limit: Optional[int] = None,
    ) -> SubmittedTx:
        """Cancel fee share.

        :param contract_address: contract address
        :param sender: sender
        :param memo: memo, defaults to None
        :param gas_limit: gas limit, defaults to None
        :return: submitted tx
        """
        # build up the cancel fee share message
        tx = Transaction()
        tx.add_message(create_cancel_feeshare_msg(sender.address(), contract_address))
        return prepare_and_broadcast_basic_transaction(
            self, tx, sender, gas_limit=gas_limit, memo=memo
        )

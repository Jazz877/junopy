import json
from dataclasses import dataclass
from typing import Iterable, Dict, Optional

import certifi
import cosmpy.aerial.client
import grpc
from cosmpy.aerial.client import prepare_and_broadcast_basic_transaction
from cosmpy.aerial.gas import GasStrategy, SimulationGasStrategy
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.tx_helpers import SubmittedTx
from cosmpy.aerial.urls import Protocol
from cosmpy.aerial.wallet import Wallet
from cosmpy.auth.rest_client import AuthRestClient
from cosmpy.bank.rest_client import BankRestClient
from cosmpy.common.rest_client import RestClient
from cosmpy.cosmwasm.rest_client import CosmWasmRestClient
from cosmpy.crypto.address import Address
from cosmpy.distribution.rest_client import DistributionRestClient
from cosmpy.params.rest_client import ParamsRestClient
from cosmpy.staking.rest_client import StakingRestClient
from cosmpy.tx.rest_client import TxRestClient

from pyuno.aerial.client.feeshare import (
    create_register_feeshare_msg,
    create_update_feeshare_msg,
    create_cancel_feeshare_msg,
)
from pyuno.aerial.client.urls import parse_url
from pyuno.feeshare.rest_client import FeeShareRestClient
from pyuno.protos.juno.feeshare.v1.query_pb2 import (
    QueryFeeSharesRequest,
    QueryFeeShareRequest,
    QueryDeployerFeeSharesRequest,
    QueryWithdrawerFeeSharesRequest,
    QueryParamsRequest,
)
from cosmpy.protos.cosmos.auth.v1beta1.query_pb2_grpc import QueryStub as AuthGrpcClient
from cosmpy.protos.cosmos.bank.v1beta1.query_pb2_grpc import QueryStub as BankGrpcClient
from cosmpy.protos.cosmos.distribution.v1beta1.query_pb2_grpc import (
    QueryStub as DistributionGrpcClient,
)
from cosmpy.protos.cosmos.params.v1beta1.query_pb2_grpc import (
    QueryStub as QueryParamsGrpcClient,
)
from cosmpy.protos.cosmos.staking.v1beta1.query_pb2_grpc import (
    QueryStub as StakingGrpcClient,
)
from cosmpy.protos.cosmos.tx.v1beta1.service_pb2_grpc import ServiceStub as TxGrpcClient
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2_grpc import (
    QueryStub as CosmWasmGrpcClient,
)
from pyuno.protos.juno.feeshare.v1.query_pb2_grpc import (
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
        self._query_interval_secs = query_interval_secs
        self._query_timeout_secs = query_timeout_secs
        cfg.validate()
        self._network_config = cfg
        self._gas_strategy: GasStrategy = SimulationGasStrategy(self)

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

            self.wasm = CosmWasmGrpcClient(grpc_client)
            self.auth = AuthGrpcClient(grpc_client)
            self.txs = TxGrpcClient(grpc_client)
            self.bank = BankGrpcClient(grpc_client)
            self.staking = StakingGrpcClient(grpc_client)
            self.distribution = DistributionGrpcClient(grpc_client)
            self.params = QueryParamsGrpcClient(grpc_client)
            self.fee_share = FeeShareGrpcClient(grpc_client)
        else:
            rest_client = RestClient(parsed_url.rest_url)

            self.wasm = CosmWasmRestClient(rest_client)  # type: ignore
            self.auth = AuthRestClient(rest_client)  # type: ignore
            self.txs = TxRestClient(rest_client)  # type: ignore
            self.bank = BankRestClient(rest_client)  # type: ignore
            self.staking = StakingRestClient(rest_client)  # type: ignore
            self.distribution = DistributionRestClient(rest_client)  # type: ignore
            self.params = ParamsRestClient(rest_client)  # type: ignore
            self.fee_share = FeeShareRestClient(rest_client)  # type: ignore

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
